"""
Cisco Configuration Generator Module

Converts Policy Manager decisions to Cisco device-agnostic format.
Focuses exclusively on Cisco IOS/NX-OS configuration generation.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from src.interfaces.config_generator import IConfigGenerator
from src.config_generator.config_model import CiscoConfig, CiscoRule, CiscoAction


class CiscoConfigGenerator(IConfigGenerator):
    """
    Converts Policy Manager decisions to Cisco device-agnostic format.
    
    Focuses exclusively on Cisco IOS/NX-OS configuration generation
    without multi-vendor complexity.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager):
        # Logging
        self.logger = logging_manager.get_logger("system")  # Info/debug logs to system.log
        self.json_logger = logging_manager.get_json_logger("config_generator")  # Per-config logs
        
        # Config
        self.config_manager = config_manager
        
        # Output directory for generated configurations
        self.output_dir = Path("configs/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Counters for unique naming
        self.acl_counter = 100
        self.class_counter = 1
        
        # Statistics
        self.stats = {
            'configurations_generated': 0,
            'total_rules_processed': 0,
            'cisco_rules_created': 0,
            'errors': 0
        }
        
        # Store last generated configuration
        self.last_configuration = None
        self.last_config_file = None
        
        self.logger.info("CiscoConfigGenerator initialized")
        print(f"--- CiscoConfigGenerator initialized")
    
    def generate_from_policies(self, policy_results: List[Dict[str, Any]]) -> str:
        """
        Convert policy results to Cisco configuration format.
        
        Args:
            policy_results: List of policy enforcement results from Policy Manager
            
        Returns:
            Cisco IOS/NX-OS configuration string
        """
        try:
            self.logger.info(f"Generating Cisco configuration from {len(policy_results)} policy results")
            
            config_lines = []
            
            # Header
            config_lines.append("! Generated Cisco Configuration")
            config_lines.append("! Generated from Policy Manager decisions")
            config_lines.append(f"! Generated at: {self._get_timestamp()}")
            config_lines.append("!")
            
            # Process each policy result
            access_lists = []
            class_maps = []
            policy_maps = []
            
            for policy in policy_results:
                cisco_config = self._convert_policy_to_cisco(policy)
                if cisco_config:
                    access_lists.extend(cisco_config.get('access_lists', []))
                    class_maps.extend(cisco_config.get('class_maps', []))
                    policy_maps.extend(cisco_config.get('policy_maps', []))
                    self.stats['total_rules_processed'] += 1
            
            # Generate Access Lists
            if access_lists:
                config_lines.append("! Access Control Lists")
                config_lines.extend(access_lists)
                config_lines.append("!")
            
            # Generate Class Maps
            if class_maps:
                config_lines.append("! Class Maps")
                config_lines.extend(class_maps)
                config_lines.append("!")
            
            # Generate Policy Maps
            if policy_maps:
                config_lines.append("! Policy Maps")
                config_lines.extend(policy_maps)
                config_lines.append("!")
            
            configuration = "\n".join(config_lines)
            
            # Save configuration to file
            config_file = self.save_configuration_to_file(configuration)
            self.last_configuration = configuration
            self.last_config_file = config_file
            
            # Log the generated configuration
            self._log_configuration_generation(policy_results, configuration)
            
            self.stats['configurations_generated'] += 1
            self.logger.info(f"Successfully generated Cisco configuration with {len(access_lists)} ACLs, {len(class_maps)} class maps, {len(policy_maps)} policy maps")
            self.logger.info(f"Configuration saved to: {config_file}")
            
            return configuration
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Failed to generate Cisco configuration: {e}")
            return f"! Error generating configuration: {e}"
    
    def generate_from_packet_contexts(self, contexts: List[PacketContext]) -> str:
        """
        Generate configuration from packet contexts that have been processed
        through the policy manager.
        
        Args:
            contexts: List of packet contexts with policy metadata
            
        Returns:
            Cisco IOS/NX-OS configuration string
        """
        try:
            self.logger.info(f"Generating Cisco configuration from {len(contexts)} packet contexts")
            
            # Extract policy results from packet contexts
            policy_results = []
            for context in contexts:
                if context.policy_metadata:
                    # Convert policy metadata to policy result format
                    policy_result = {
                        'action_taken': context.policy_metadata.get('action', 'allow'),
                        'action_parameters': context.policy_metadata.get('parameters', {}),
                        'flow_key': context.get_flow_key(),
                        'packet_info': {
                            'src_ip': context.packet.src_ip,
                            'dst_ip': context.packet.dst_ip,
                            'src_port': context.packet.src_port,
                            'dst_port': context.packet.dst_port,
                            'protocol': context.packet.protocol
                        }
                    }
                    policy_results.append(policy_result)
            
            return self.generate_from_policies(policy_results)
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Failed to generate configuration from packet contexts: {e}")
            return f"! Error generating configuration: {e}"
    
    def get_supported_vendors(self) -> List[str]:
        """Get list of supported vendor/device types."""
        return ["cisco", "cisco_ios", "cisco_nxos"]
    
    def get_configuration_format(self) -> str:
        """Get the configuration format/type this generator produces."""
        return "cisco_ios"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration generator statistics."""
        return self.stats.copy()
    
    def save_configuration_to_file(self, configuration: str, filename: Optional[str] = None) -> str:
        """
        Save generated configuration to a file.
        
        Args:
            configuration: The Cisco configuration string to save
            filename: Optional filename, will generate timestamped name if not provided
            
        Returns:
            str: Path to the saved configuration file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cisco_config_{timestamp}.cfg"
            
            config_file = self.output_dir / filename
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(configuration)
            
            self.logger.info(f"Configuration saved to: {config_file}")
            return str(config_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to file: {e}")
            raise
    
    def get_last_configuration(self) -> Optional[str]:
        """Get the last generated configuration."""
        return self.last_configuration
    
    def get_last_config_file(self) -> Optional[str]:
        """Get the path to the last saved configuration file."""
        return self.last_config_file
    
    def list_generated_configs(self) -> List[str]:
        """List all generated configuration files."""
        try:
            config_files = []
            for file in self.output_dir.glob("*.cfg"):
                config_files.append(str(file))
            return sorted(config_files)
        except Exception as e:
            self.logger.error(f"Failed to list configuration files: {e}")
            return []
    
    def _convert_policy_to_cisco(self, policy: Dict[str, Any]) -> Dict[str, List[str]]:
        """Convert single policy to Cisco configuration elements."""
        try:
            action = policy.get('action_taken', 'allow')
            action_params = policy.get('action_parameters', {})
            packet_info = policy.get('packet_info', {})
            
            config = {
                'access_lists': [],
                'class_maps': [],
                'policy_maps': []
            }
            
            # Create more specific ACLs based on packet information
            src_ip = packet_info.get('src_ip', 'any')
            dst_ip = packet_info.get('dst_ip', 'any')
            src_port = packet_info.get('src_port')
            dst_port = packet_info.get('dst_port')
            protocol = packet_info.get('protocol', 'ip')
            
            if action == 'block':
                # Generate deny ACL
                acl_line = self._create_acl_line('deny', protocol, src_ip, dst_ip, src_port, dst_port)
                config['access_lists'].append(acl_line)
                self.acl_counter += 1
                
            elif action == 'allow':
                # Generate permit ACL
                acl_line = self._create_acl_line('permit', protocol, src_ip, dst_ip, src_port, dst_port)
                config['access_lists'].append(acl_line)
                self.acl_counter += 1
                
            elif action == 'throttle':
                # Generate QoS configuration
                bandwidth = action_params.get('bandwidth_mbps', 1)
                class_name = f"THROTTLE_CLASS_{self.class_counter}"
                policy_name = f"THROTTLE_POLICY_{self.class_counter}"
                
                # Class map
                config['class_maps'].extend([
                    f"class-map match-all {class_name}",
                    f" match access-group {self.acl_counter}"
                ])
                
                # Policy map
                config['policy_maps'].extend([
                    f"policy-map {policy_name}",
                    f" class {class_name}",
                    f"  police {bandwidth}000000 conform-action transmit exceed-action drop"
                ])
                
                # ACL for matching
                acl_line = self._create_acl_line('permit', protocol, src_ip, dst_ip, src_port, dst_port)
                config['access_lists'].append(acl_line)
                
                self.acl_counter += 1
                self.class_counter += 1
                
            elif action == 'prioritize':
                # Generate DSCP marking
                priority = action_params.get('priority', 0)
                dscp_value = self._priority_to_dscp(priority)
                class_name = f"PRIORITY_CLASS_{self.class_counter}"
                policy_name = f"PRIORITY_POLICY_{self.class_counter}"
                
                # Class map
                config['class_maps'].extend([
                    f"class-map match-all {class_name}",
                    f" match access-group {self.acl_counter}"
                ])
                
                # Policy map
                config['policy_maps'].extend([
                    f"policy-map {policy_name}",
                    f" class {class_name}",
                    f"  set dscp {dscp_value}"
                ])
                
                # ACL for matching
                acl_line = self._create_acl_line('permit', protocol, src_ip, dst_ip, src_port, dst_port)
                config['access_lists'].append(acl_line)
                
                self.acl_counter += 1
                self.class_counter += 1
            
            self.stats['cisco_rules_created'] += 1
            return config
            
        except Exception as e:
            self.logger.error(f"Error converting policy to Cisco config: {e}")
            return {'access_lists': [], 'class_maps': [], 'policy_maps': []}
    
    def _create_acl_line(self, action: str, protocol: str, src_ip: str, dst_ip: str, 
                        src_port: Optional[int] = None, dst_port: Optional[int] = None) -> str:
        """Create a Cisco ACL line with proper formatting."""
        if protocol.lower() in ['tcp', 'udp'] and (src_port or dst_port):
            src_port_str = f"eq {src_port}" if src_port else ""
            dst_port_str = f"eq {dst_port}" if dst_port else ""
            return f"access-list {self.acl_counter} {action} {protocol} {src_ip} {src_port_str} {dst_ip} {dst_port_str}".strip()
        else:
            return f"access-list {self.acl_counter} {action} {protocol} {src_ip} {dst_ip}"
    
    def _priority_to_dscp(self, priority: int) -> str:
        """Convert priority level to DSCP value."""
        dscp_map = {
            0: "ef",      # Expedited Forwarding (voice)
            1: "af41",    # Assured Forwarding Class 4
            2: "af31",    # Assured Forwarding Class 3
            3: "be"       # Best Effort
        }
        return dscp_map.get(priority, "be")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for configuration headers."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_configuration_generation(self, policy_results: List[Dict[str, Any]], configuration: str) -> None:
        """Log configuration generation details."""
        log_data = {
            "timestamp": self._get_timestamp(),
            "policy_count": len(policy_results),
            "configuration_length": len(configuration),
            "acl_count": configuration.count("access-list"),
            "class_map_count": configuration.count("class-map"),
            "policy_map_count": configuration.count("policy-map"),
            "stats": self.stats.copy()
        }
        self.json_logger.log_json(log_data)
