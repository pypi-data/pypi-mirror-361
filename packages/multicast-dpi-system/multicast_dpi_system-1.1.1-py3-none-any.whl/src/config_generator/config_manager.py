"""
Configuration Manager for Automatic Configuration Generation

Handles automatic configuration generation from packet contexts with buffering,
periodic generation, and integration with the main system pipeline.
"""
import time
from typing import List, Dict, Any, Optional, Callable
from collections import deque
from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.interfaces.config_generator import IConfigGenerator


class ConfigurationManager:
    """
    Manages automatic configuration generation from packet contexts.
    
    Features:
    - Buffers packet contexts with policy metadata
    - Generates configurations periodically or on demand
    - Supports different generation triggers
    - Integrates with the main system pipeline
    """
    
    def __init__(self, 
                 config_generator: IConfigGenerator,
                 logging_manager: LoggingManager,
                 config_manager: ConfigManager,
                 buffer_size: int = 1000,
                 generation_interval_packets: int = 1000,
                 max_buffer_age_seconds: int = 300):
        
        # Core components
        self.config_generator = config_generator
        self.logging_manager = logging_manager
        self.config_manager = config_manager
        self.logger = logging_manager.get_logger("system")
        
        # Configuration
        self.buffer_size = buffer_size
        self.generation_interval_packets = generation_interval_packets
        self.max_buffer_age_seconds = max_buffer_age_seconds
        
        # Packet context buffer
        self.packet_buffer: deque = deque(maxlen=buffer_size)
        self.last_generation_time = time.time()
        self.last_generation_packet_count = 0
        
        # Statistics
        self.stats = {
            'packets_buffered': 0,
            'configurations_generated': 0,
            'buffer_overflows': 0,
            'generation_errors': 0,
            'last_generation_duration_ms': 0
        }
        
        self.logger.info("ConfigurationManager initialized")
    
    def process_packet_context(self, context: PacketContext) -> None:
        """
        Process a packet context and potentially trigger configuration generation.
        
        Args:
            context: Packet context with policy metadata
        """
        try:
            # Add to buffer if it has policy metadata
            if context.policy_metadata:
                self.packet_buffer.append({
                    'context': context,
                    'timestamp': time.time(),
                    'packet_count': self.stats['packets_buffered']
                })
                self.stats['packets_buffered'] += 1
                
                # Check if we should generate configuration
                if self._should_generate_configuration():
                    self._generate_configuration_from_buffer()
            
        except Exception as e:
            self.logger.error(f"Error processing packet context: {e}")
            self.stats['generation_errors'] += 1
    
    def _should_generate_configuration(self) -> bool:
        """Determine if configuration should be generated based on triggers."""
        current_time = time.time()
        current_packet_count = self.stats['packets_buffered']
        
        # Check packet count interval
        packet_interval_reached = (current_packet_count - self.last_generation_packet_count) >= self.generation_interval_packets
        
        # Check time interval
        time_interval_reached = (current_time - self.last_generation_time) >= self.max_buffer_age_seconds
        
        # Check buffer fullness
        buffer_full = len(self.packet_buffer) >= self.buffer_size * 0.8
        
        return packet_interval_reached or time_interval_reached or buffer_full
    
    def _generate_configuration_from_buffer(self) -> None:
        """Generate configuration from buffered packet contexts."""
        try:
            start_time = time.time()
            
            if not self.packet_buffer:
                self.logger.debug("No packet contexts in buffer to generate configuration")
                return
            
            self.logger.info(f"Generating configuration from {len(self.packet_buffer)} buffered packet contexts")
            
            # Extract policy results from packet contexts
            policy_results = []
            for buffer_entry in self.packet_buffer:
                context = buffer_entry['context']
                if context.policy_metadata:
                    policy_result = self._convert_context_to_policy_result(context)
                    policy_results.append(policy_result)
            
            if policy_results:
                # Generate configuration
                config = self.config_generator.generate_from_policies(policy_results)
                config_file = self.config_generator.get_last_config_file()
                
                # Update statistics
                generation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                self.stats['configurations_generated'] += 1
                self.stats['last_generation_duration_ms'] = generation_time
                self.last_generation_time = time.time()
                self.last_generation_packet_count = self.stats['packets_buffered']
                
                # Clear buffer after successful generation
                self.packet_buffer.clear()
                
                self.logger.info(f"Generated configuration with {len(config.split(chr(10)))} lines in {generation_time:.2f}ms")
                print(f"📄 Generated Cisco configuration saved to: {config_file}")
                
            else:
                self.logger.debug("No valid policy results found in buffer")
                
        except Exception as e:
            self.logger.error(f"Error generating configuration from buffer: {e}")
            self.stats['generation_errors'] += 1
    
    def _convert_context_to_policy_result(self, context: PacketContext) -> Dict[str, Any]:
        """Convert packet context to policy result format."""
        return {
            'action_taken': context.policy_metadata.get('action', 'allow'),
            'action_parameters': context.policy_metadata.get('parameters', {}),
            'flow_key': context.get_flow_key(),
            'packet_info': {
                'src_ip': context.packet.src_ip,
                'dst_ip': context.packet.dst_ip,
                'src_port': context.packet.src_port,
                'dst_port': context.packet.dst_port,
                'protocol': context.packet.protocol
            },
            'classification_info': context.classification_metadata,
            'dpi_info': context.dpi_metadata
        }
    
    def force_generation(self) -> Optional[str]:
        """Force configuration generation from current buffer."""
        try:
            self._generate_configuration_from_buffer()
            return self.config_generator.get_last_config_file()
        except Exception as e:
            self.logger.error(f"Error in forced configuration generation: {e}")
            return None
    
    def get_buffer_info(self) -> Dict[str, Any]:
        """Get information about the current buffer state."""
        return {
            'buffer_size': len(self.packet_buffer),
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': len(self.packet_buffer) / self.buffer_size,
            'oldest_entry_age_seconds': time.time() - self.packet_buffer[0]['timestamp'] if self.packet_buffer else 0,
            'last_generation_time': self.last_generation_time,
            'packets_since_last_generation': self.stats['packets_buffered'] - self.last_generation_packet_count
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive configuration manager statistics."""
        buffer_info = self.get_buffer_info()
        config_stats = self.config_generator.get_statistics()
        
        return {
            'manager': self.stats.copy(),
            'buffer': buffer_info,
            'generator': config_stats,
            'configuration': {
                'buffer_size': self.buffer_size,
                'generation_interval_packets': self.generation_interval_packets,
                'max_buffer_age_seconds': self.max_buffer_age_seconds
            }
        }
    
    def show_configuration_info(self) -> None:
        """Display information about generated configurations."""
        try:
            config_files = self.config_generator.list_generated_configs()
            last_config = self.config_generator.get_last_configuration()
            last_file = self.config_generator.get_last_config_file()
            buffer_info = self.get_buffer_info()
            
            print(f"\n📁 Configuration Manager Info:")
            print(f"   - Output directory: {self.config_generator.output_dir.absolute()}")
            print(f"   - Buffer utilization: {buffer_info['buffer_utilization']:.1%}")
            print(f"   - Packets in buffer: {buffer_info['buffer_size']}")
            print(f"   - Total configurations generated: {len(config_files)}")
            print(f"   - Last configuration file: {last_file}")
            
            if config_files:
                print(f"   - Available configuration files:")
                for i, file in enumerate(config_files[-5:], 1):  # Show last 5 files
                    print(f"     {i}. {file}")
            
            if last_config:
                lines = last_config.split('\n')
                print(f"   - Last configuration preview (first 10 lines):")
                for i, line in enumerate(lines[:10], 1):
                    print(f"     {i:2d}: {line}")
                if len(lines) > 10:
                    print(f"     ... ({len(lines) - 10} more lines)")
                    
        except Exception as e:
            print(f"❌ Error getting configuration info: {e}")
    
    def shutdown(self) -> None:
        """Shutdown the configuration manager and generate final configuration."""
        try:
            self.logger.info("Shutting down ConfigurationManager...")
            
            # Generate final configuration from remaining buffer
            if self.packet_buffer:
                self.logger.info(f"Generating final configuration from {len(self.packet_buffer)} remaining packet contexts")
                self._generate_configuration_from_buffer()
            
            # Display final statistics
            stats = self.get_statistics()
            print(f"\n📊 Configuration Manager Final Stats:")
            print(f"   - Packets buffered: {stats['manager']['packets_buffered']}")
            print(f"   - Configurations generated: {stats['manager']['configurations_generated']}")
            print(f"   - Generation errors: {stats['manager']['generation_errors']}")
            print(f"   - Avg generation time: {stats['manager']['last_generation_duration_ms']:.2f}ms")
            
            self.logger.info("ConfigurationManager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during ConfigurationManager shutdown: {e}") 