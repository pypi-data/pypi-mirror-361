"""
Main entry point for the Packet Capture Module.
Provides a clean, structured interface for the DPI system.
"""
import threading
import time
from collections import defaultdict
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from src.utils.logging_utils import LoggingManager, PacketLogger
from src.utils.config_handler import ConfigManager
from src.core.packet import Packet
from src.core.packet_context import PacketContext
from src.packet_capture.multicast_listener import MulticastListener
from src.packet_capture.filter_engine import FilterEngine
from src.packet_capture.packet_buffer import PacketBuffer
from src.interfaces.packet_capture import IPacketCapture


@dataclass
class SystemStats:
    """System statistics container"""
    total_packets_captured: int = 0
    total_packets_processed: int = 0
    total_packets_dropped_filter: int = 0
    total_packets_dropped_buffer: int = 0
    total_packets_logged: int = 0
    protocol_stats: Dict = field(default_factory=lambda: defaultdict(int))


class LivePacketCapture(IPacketCapture):
    """
    Main packet capture system that orchestrates all components.
    Provides a clean, structured interface for the DPI system.
    """
    
    def __init__(self, config_file: str, logging_manager: LoggingManager, config_manager: ConfigManager):
        """Initialize the packet capture system with configuration"""
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.json_logger = logging_manager.get_json_logger(self.__class__.__name__)
        self.config_manager = config_manager
        
        # Load the packet capture config - it's merged into the main config
        self.config = self.config_manager._configs
        
        self._running = False
        self._shutdown_called = False
        self._downstream_callback: Optional[Callable[[PacketContext], None]] = None
        
        self.listener: Optional[MulticastListener] = None
        buffer_config = self.config.get('buffer', {})
        filter_config = self.config.get('filter', {})
        listener_config = {
            'interface': self.config.get('interface'),
            'multicast_ips': self.config.get('multicast_ips', []),
            'ports': self.config.get('ports'),
            'bpf_filter': None  # Will be set after filter_engine is created
        }
        self.buffer = PacketBuffer(logging_manager=logging_manager, buffer_config=buffer_config)
        self.filter_engine = FilterEngine(logging_manager=logging_manager, filter_config=filter_config)
        # After filter_engine is created, set bpf_filter in listener_config
        listener_config['bpf_filter'] = self.filter_engine.get_bpf_string()
        self.listener = MulticastListener(logging_manager=logging_manager, **listener_config)
        
        # PacketLogger is for packet data, not module logs. It remains separate.
        self.packet_logger = None 
        if self.config.get('logging', {}).get('enable_packet_logging', False):
            self.packet_logger = PacketLogger(
                log_file=self.config.get('logging', {}).get('log_file', 'packet_data.log'),
                format_type=self.config.get('logging', {}).get('format', 'json'),
            )
        
        self.stats = SystemStats()
        
        self.processing_thread: Optional[threading.Thread] = None
        self.stats_thread: Optional[threading.Thread] = None
        
        self.logger.info(f"PacketCaptureSystem initialized with config: {config_file}")
    
    def initialize(self) -> bool:
        """Initialize the system components"""
        try:
            self.logger.info("System initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def _update_statistics(self, packet: Packet) -> None:
        """Update system statistics with packet information"""
        self.stats.protocol_stats[packet.protocol] += 1
    
    def _packet_handler(self, context: PacketContext) -> None:
        """
        Handle incoming packet contexts from the multicast listener.
        This is the main entry point for packets into the capture system.
        """
        try:
            self.stats.total_packets_captured += 1
            context.mark_entry('capture_system')

            # The packet is inside the context, no need to extract it here
            self._update_statistics(context.packet)
            
            if not self.filter_engine.apply_filter(context.packet):
                self.stats.total_packets_dropped_filter += 1
                print(f"⚠️  Packet dropped by filter: {context.packet.src_ip}:{context.packet.src_port} -> {context.packet.dst_ip}:{context.packet.dst_port} [{context.packet.protocol}]")
                return

            # Pass the entire context to the buffer
            if not self.buffer.add_packet(context):
                self.stats.total_packets_dropped_buffer += 1
                print(f"⚠️  Packet dropped by buffer: {context.packet.src_ip}:{context.packet.src_port} -> {context.packet.dst_ip}:{context.packet.dst_port} [{context.packet.protocol}]")
                return
            
            # Log per-packet JSON data to packet_capture.log
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "packet_id": context.packet_id,
                "src_ip": context.packet.src_ip,
                "dst_ip": context.packet.dst_ip,
                "src_port": context.packet.src_port,
                "dst_port": context.packet.dst_port,
                "protocol": context.packet.protocol,
                "length": context.packet.length,
                "interface": context.packet.interface
            }
            self.json_logger.log_json(log_data)

        except Exception as e:
            self.logger.error(f"Error handling packet: {e}", exc_info=True)
    
    def _processing_loop(self) -> None:
        """Process packets from the buffer"""
        while self._running:
            try:
                # The buffer now returns a full context
                context = self.buffer.get_next_packet()
                if context:
                    self.stats.total_packets_processed += 1
                    
                    if self._downstream_callback:
                        self._downstream_callback(context)
                
                time.sleep(self.config.get('processing', {}).get('interval_sec', 0.1))
                
            except Exception as e:
                self.logger.error(f"Buffer processing error: {e}", exc_info=True)
    
    def _stats_loop(self) -> None:
        """Log system statistics periodically"""
        while self._running:
            try:
                # Print simple one-line statistics to console
                print(self._get_simple_statistics(), end='\\r')
                time.sleep(3.0)
            except Exception as e:
                self.logger.error(f"Statistics logging error: {e}", exc_info=True)

    def _get_simple_statistics(self) -> str:
        """Get simple one-line statistics for console output"""
        buffer_stats = self.buffer.get_stats()
        total_dropped = self.stats.total_packets_dropped_filter + self.stats.total_packets_dropped_buffer
        drop_rate = (total_dropped / self.stats.total_packets_captured * 100) if self.stats.total_packets_captured > 0 else 0
        
        return (f"📊 Captured: {self.stats.total_packets_captured:,} | "
                f"Processed: {self.stats.total_packets_processed:,} | "
                f"Dropped: {total_dropped:,} ({drop_rate:.1f}%)")
    
    def _format_statistics_output(self) -> str:
        """Format statistics for console output"""
        lines = []
        lines.append("=" * 50)
        lines.append("PACKET CAPTURE SYSTEM - FINAL STATISTICS")
        lines.append("=" * 50)
        
        # Capture statistics
        lines.append(f"\n📊 CAPTURE STATISTICS:")
        lines.append(f"   Total packets captured: {self.stats.total_packets_captured:,}")
        lines.append(f"   Total packets processed: {self.stats.total_packets_processed:,}")
        total_dropped = self.stats.total_packets_dropped_filter + self.stats.total_packets_dropped_buffer
        lines.append(f"   Total packets dropped: {total_dropped:,}")
        lines.append(f"   Total packets logged: {self.stats.total_packets_logged:,}")
        
        if self.stats.total_packets_captured > 0:
            drop_rate = (total_dropped / self.stats.total_packets_captured) * 100
            lines.append(f"   Drop rate: {drop_rate:.2f}%")
        
        # Protocol distribution
        lines.append(f"\n🌐 PROTOCOL DISTRIBUTION:")
        for protocol, count in sorted(
            self.stats.protocol_stats.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]:
            percentage = (count / self.stats.total_packets_captured * 100) if self.stats.total_packets_captured > 0 else 0
            lines.append(f"   {protocol}: {count:,} packets ({percentage:.1f}%)")
        
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)
    
    def print_final_statistics(self) -> None:
        """Print comprehensive statistics at shutdown"""
        print(self._format_statistics_output())
    
    def _start_background_threads(self) -> None:
        """Start background processing threads"""
        self.processing_thread = threading.Thread(target=self._processing_loop, name="PacketProcessor", daemon=True)
        self.stats_thread = threading.Thread(target=self._stats_loop, name="StatsLogger", daemon=True)
        self.processing_thread.start()
        self.stats_thread.start()
    
    def _log_startup_info(self) -> None:
        """Log startup information"""
        # Show filter information from the config handler
        filter_config = self.config.get('filter', {})
        if filter_config.get('enable', False):
            self.logger.info("Filtering is enabled")
        else:
            self.logger.info("Filtering is disabled")
            
    def start(self, callback: Callable[[PacketContext], None]) -> bool:
        """Start the packet capture and processing"""
        if self._running:
            self.logger.warning("System is already running.")
            return True
        self._running = True
        self._downstream_callback = callback

        if self.initialize():
            self.listener.start_capture(self._packet_handler)
            self._start_background_threads()
            self._log_startup_info()
            return True
        else:
            self.logger.error("System startup failed during initialization.")
            self._running = False
            return False

    @property
    def is_running(self) -> bool:
        """Check if the system is running"""
        return self._running

    def stop(self) -> None:
        """Stop the packet capture and processing"""
        if self._shutdown_called:
            return
        
        self.logger.info("Shutting down packet capture system...")
        self._shutdown_called = True
        self._running = False
        
        # Stop listener and buffer
        if self.listener:
            self.listener.stop_capture()
        if self.buffer:
            self.buffer.shutdown()
        self.print_final_statistics()

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self._running,
            'stats': {
                'total_packets_captured': self.stats.total_packets_captured,
                'total_packets_processed': self.stats.total_packets_processed,
                'total_packets_dropped': self.stats.total_packets_dropped_filter + self.stats.total_packets_dropped_buffer,
                'total_packets_logged': self.stats.total_packets_logged
            },
            'buffer_stats': self.buffer.get_stats() if self.buffer else {}
        } 