"""
Multicast Listener implementation for Linux using pyshark with centralized config support.
"""
import threading
import time
import os
import subprocess
from typing import Callable, Optional, Dict, Any
from pathlib import Path
import pyshark
from src.core.packet import Packet
from src.core.factory import PacketFactory
from src.utils.logging_utils import LoggingManager

class MulticastListener:
    def __init__(
        self,
        interface: Optional[str],
        multicast_ips: Optional[list],
        ports: Optional[list],
        bpf_filter: Optional[str],
        logging_manager: LoggingManager
    ):
        """
        Initialize multicast listener with centralized config support.
        
        Args:
            interface: Network interface to listen on (overrides config)
            multicast_ips: List of multicast IPs to filter (overrides config)
            ports: List of ports to filter (overrides config)
            bpf_filter: BPF filter to apply at capture time (optional)
            logging_manager: The centralized logging manager.
        """
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.interface = interface
        self.multicast_ips = multicast_ips or []
        self.ports = ports
        self.capture = None
        self.capture_thread = None
        self.running = False
        self.callback = None
        self._lock = threading.Lock()
        self.bpf_filter = bpf_filter
        
        # Try to find a suitable interface if none specified
        if not self.interface:
            self.interface = self._find_suitable_interface()
            
        self.logger.info(f"Initialized MulticastListener with interface: {self.interface}")
    
    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        Ensures resources are cleaned up even if an exception occurs.
        """
        self.stop_capture()
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
        return False

    def _generate_bpf_filter(self) -> str:
        """Generate BPF filter from configuration."""
        filters = []
        
        # IP filters
        if self.multicast_ips:
            ip_filters = [f'dst host {ip}' for ip in self.multicast_ips]
            if ip_filters:
                filters.append(f'({" or ".join(ip_filters)})')
        
        # Port filters
        if self.ports:
            port_filters = [f'dst port {port}' for port in self.ports]
            if port_filters:
                filters.append(f'({" or ".join(port_filters)})')
        
        # Combine filters or use default multicast filter
        if filters:
            return ' and '.join(filters)
        
        # Default BPF filter for multicast
        return 'ip multicast'

    def start_capture(self, callback: Callable[[Packet], None]) -> bool:
        """
        Start multicast packet capture with configured settings.
        """
        if self.running:
            self.logger.warning("Capture already running")
            return False

        try:
            # Check TShark availability first
            if not self._check_tshark_availability():
                return False
                
            generated_filter = self._generate_bpf_filter()
            user_filter = self.bpf_filter or ''

            # Combine filters if both are present
            if generated_filter and user_filter:
                final_bpf_filter = f'({generated_filter}) and ({user_filter})'
            elif generated_filter:
                final_bpf_filter = generated_filter
            else:
                final_bpf_filter = user_filter

            self.logger.info(f"Starting capture with BPF filter: {final_bpf_filter}")
            
            # Add debug information
            if not self.interface:
                self.logger.error("No interface specified for capture")
                return False
                
            self.logger.info(f"Using interface: {self.interface}")
            
            # Try to create capture with error handling
            try:
                self.capture = pyshark.LiveCapture(
                    interface=self.interface,
                    bpf_filter=final_bpf_filter,
                    use_json=True,
                    include_raw=True,
                    display_filter=''
                )
            except Exception as capture_error:
                self.logger.error(f"Failed to create pyshark capture: {capture_error}")
                self.logger.error("This might be due to:")
                self.logger.error("1. Interface doesn't exist")
                self.logger.error("2. Insufficient permissions (try running with sudo)")
                self.logger.error("3. TShark not installed or not in PATH")
                return False
            
            self.callback = callback
            self.running = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                name=f"MulticastListener-{self.interface}",
                daemon=True
            )
            self.capture_thread.start()
            
            time.sleep(0.2)
            if not self.capture_thread.is_alive():
                raise RuntimeError("Capture thread failed to start")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start capture: {e}", exc_info=True)
            self.stop_capture()
            return False

    def _capture_loop(self):
        """Main capture loop running in background thread."""
        try:
            for pyshark_packet in self.capture.sniff_continuously(packet_count=0):
                if not self.running:
                    break
                    
                try:
                    if not hasattr(pyshark_packet, 'frame_raw'):
                        continue
                        
                    raw_data = bytes.fromhex(pyshark_packet.frame_raw.value)
                    
                    # Use the factory to create the packet and context
                    packet, context = PacketFactory.create_packet_with_context(
                        raw_data=raw_data,
                        timestamp=pyshark_packet.sniff_time.timestamp(),
                        interface=self.interface
                    )
                    
                    if self.callback:
                        # Pass the context to the callback, not the raw packet
                        self.callback(context)
                        
                except Exception as e:
                    self.logger.error(f"Error processing packet: {e}", exc_info=True)
                    
        except Exception as e:
            self.logger.error(f"Capture loop error: {e}", exc_info=True)
        finally:
            self.stop_capture()

    def stop_capture(self):
        """Stop the capture and clean up resources."""
        with self._lock:
            if not self.running:
                return
                
            self.running = False
            
            try:
                if self.capture:
                    self.capture.close()
            except Exception as e:
                self.logger.error(f"Error closing capture: {e}", exc_info=True)
            
            try:
                if (self.capture_thread and 
                    threading.current_thread() is not self.capture_thread and
                    self.capture_thread.is_alive()):
                    self.capture_thread.join(timeout=5)
                    if self.capture_thread.is_alive():
                        self.logger.warning("Capture thread did not stop cleanly")
            except Exception as e:
                self.logger.error(f"Error joining thread: {e}", exc_info=True)
                
            self.logger.info("Multicast capture stopped")

    @property
    def current_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            'interface': self.interface,
            'multicast_ips': self.multicast_ips,
            'ports': self.ports
        }

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.stop_capture()

    def _find_suitable_interface(self) -> Optional[str]:
        """Find a suitable network interface for capture."""
        try:
            # Try to get list of interfaces using ip command
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':' in line and 'state UP' in line:
                        # Extract interface name (e.g., "1: lo: <LOOPBACK,UP,LOWER_UP>")
                        parts = line.split(':')
                        if len(parts) >= 2:
                            interface_name = parts[1].strip()
                            # Skip loopback and virtual interfaces
                            if not interface_name.startswith('lo') and not interface_name.startswith('docker'):
                                self.logger.info(f"Found suitable interface: {interface_name}")
                                return interface_name
            
            # Fallback: try common interface names
            common_interfaces = ['eth0', 'wlan0', 'wlp0s20f3', 'enp0s3', 'ens33']
            for iface in common_interfaces:
                try:
                    result = subprocess.run(['ip', 'link', 'show', iface], capture_output=True)
                    if result.returncode == 0:
                        self.logger.info(f"Found interface: {iface}")
                        return iface
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error finding interface: {e}")
            
        self.logger.warning("No suitable interface found")
        return None
    
    def _check_tshark_availability(self) -> bool:
        """Check if TShark is available on the system."""
        try:
            result = subprocess.run(['tshark', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("TShark is available")
                return True
            else:
                self.logger.error("TShark is not available")
                return False
        except FileNotFoundError:
            self.logger.error("TShark not found. Please install Wireshark/tshark:")
            self.logger.error("  Ubuntu/Debian: sudo apt-get install tshark")
            self.logger.error("  CentOS/RHEL: sudo yum install wireshark")
            self.logger.error("  macOS: brew install wireshark")
            return False
        except Exception as e:
            self.logger.error(f"Error checking TShark availability: {e}")
            return False