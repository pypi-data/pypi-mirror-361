"""
DPI Engine - Simple Pipeline Coordinator

This module coordinates the three DPI analysis modules in sequence:
1. Protocol Identifier (application protocols)
2. Encrypted Analyzer (basic encryption detection)
3. Signature Matcher (pattern matching)

Each module adds its specific metadata to the packet context.
"""
from typing import Dict, Any
from collections import defaultdict
from src.core.packet_context import PacketContext
from src.interfaces.dpi_engine import DPIEngineInterface
from src.dpi_engine.protocol_identifier import create_protocol_identifier
from src.dpi_engine.encrypted_analyzer import create_encrypted_analyzer
from src.dpi_engine.signature_matcher import create_signature_matcher
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from datetime import datetime


class DPIEngine(DPIEngineInterface):
    """
    Simple pipeline coordinator for DPI analysis modules.
    
    Runs each module in sequence, allowing each to add its metadata
    to the packet context without overlap.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager, signatures_file: str):
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.json_logger = logging_manager.get_json_logger(self.__class__.__name__)
        
        # Get configs for each module
        pi_config = config_manager.get_module_config('protocol_identifier')
        ea_config = config_manager.get_module_config('encrypted_analyzer')
        sm_config = config_manager.get_module_config('signature_matcher')
        
        # Initialize the three analysis modules with dedicated loggers and configs
        self.protocol_identifier = create_protocol_identifier(
            logging_manager,
            pi_config
        )
        self.encrypted_analyzer = create_encrypted_analyzer(
            logging_manager,
            ea_config
        )
        self.signature_matcher = create_signature_matcher(
            logging_manager,
            sm_config,
            signatures_file
        )
        
        # Statistics tracking
        self.stats = {
            'packets_analyzed': 0,
            'protocols_identified': 0,
            'encrypted_detected': 0,
            'signatures_matched': 0,
            'protocol_distribution': defaultdict(int),
            'codec_distribution': defaultdict(int)
        }
        
        self.logger.info("DPI Engine initialized")
    
    def analyze_packet(self, context: PacketContext) -> None:
        """
        Run packet through the DPI analysis pipeline.
        
        Each module adds its specific metadata:
        - protocol_identification: Application protocols
        - encryption_analysis: Basic encryption detection
        - signature_matching: Pattern matches
        """
        try:
            # Mark overall DPI analysis start
            context.mark_entry('dpi_engine')
            
            # Step 1: Protocol identification
            self.protocol_identifier.identify_protocol(context)
            
            # Step 2: Encryption analysis
            self.encrypted_analyzer.analyze_encryption(context)
            
            # Step 3: Signature matching
            self.signature_matcher.match_signatures(context)
            
            # Mark overall DPI analysis end
            context.mark_exit('dpi_engine')
            
            # Update statistics
            self.stats['packets_analyzed'] += 1
            
            # Count protocol identifications and track distribution
            protocol_info = context.dpi_metadata.get('protocol_identification', {})
            if protocol_info.get('application_protocol') or protocol_info.get('codec'):
                self.stats['protocols_identified'] += 1
                
                # Track protocol distribution
                if protocol_info.get('application_protocol'):
                    self.stats['protocol_distribution'][protocol_info['application_protocol']] += 1
                
                # Track codec distribution
                if protocol_info.get('codec'):
                    self.stats['codec_distribution'][protocol_info['codec']] += 1
            
            # Count encryption detections
            encryption_info = context.dpi_metadata.get('encryption_analysis', {})
            if encryption_info.get('is_encrypted'):
                self.stats['encrypted_detected'] += 1
            
            # Count signature matches
            signature_info = context.dpi_metadata.get('signature_matching', {})
            if signature_info.get('matched'):
                self.stats['signatures_matched'] += 1
            
            # Log per-packet JSON data to dpi_engine.log
            log_data = {
                "packet_id": context.packet_id,
                "timestamp": datetime.now().isoformat(),
                "dpi_metadata": context.dpi_metadata
            }
            self.json_logger.log_json(log_data)
            
        except Exception as e:
            self.logger.error(f"Error in DPI engine analysis: {e}")
            context.add_error('dpi_engine', str(e))
    
    def get_module_stats(self) -> Dict[str, Any]:
        """Get statistics from all modules"""
        return {
            'protocol_identifier': self.protocol_identifier.get_stats(),
            'encrypted_analyzer': self.encrypted_analyzer.get_stats(),
            'signature_matcher': self.signature_matcher.get_stats()
        }
    
    def print_final_statistics(self):
        """Print final DPI engine statistics"""
        if self.stats['packets_analyzed'] == 0:
            return
        
        print("=" * 50)
        print("🔍 DPI ENGINE STATISTICS:")
        print("=" * 50)
        
        # Overall statistics
        total_packets = self.stats['packets_analyzed']
        protocol_rate = (self.stats['protocols_identified'] / total_packets * 100) if total_packets > 0 else 0
        encryption_rate = (self.stats['encrypted_detected'] / total_packets * 100) if total_packets > 0 else 0
        signature_rate = (self.stats['signatures_matched'] / total_packets * 100) if total_packets > 0 else 0
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Total packets analyzed: {total_packets:,}")
        print(f"   Protocols identified: {self.stats['protocols_identified']:,} ({protocol_rate:.1f}%)")
        print(f"   Encrypted traffic detected: {self.stats['encrypted_detected']:,} ({encryption_rate:.1f}%)")
        print(f"   Signatures matched: {self.stats['signatures_matched']:,} ({signature_rate:.1f}%)")
        
        # Protocol distribution
        if self.stats['protocol_distribution']:
            print(f"\n🌐 PROTOCOL DISTRIBUTION:")
            for protocol, count in sorted(
                self.stats['protocol_distribution'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]:
                percentage = (count / total_packets * 100) if total_packets > 0 else 0
                print(f"   {protocol}: {count:,} packets ({percentage:.1f}%)")
        
        # Codec distribution
        if self.stats['codec_distribution']:
            print(f"\n🌐 CODEC DISTRIBUTION:")
            for codec, count in sorted(
                self.stats['codec_distribution'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]:
                percentage = (count / total_packets * 100) if total_packets > 0 else 0
                print(f"   {codec}: {count:,} packets ({percentage:.1f}%)")
        print("\n")
        print("=" * 50)
    
    def shutdown(self):
        """Shutdown all DPI modules"""
        try:
            self.protocol_identifier.shutdown()
            self.encrypted_analyzer.shutdown()
            self.signature_matcher.shutdown()
            
            # Print final statistics
            print("\n")
            self.logger.info("DPI Engine shutdown complete")
            self.print_final_statistics()
            
        except Exception as e:
            self.logger.error(f"Error during DPI engine shutdown: {e}")


# Factory function to create DPI engine instance
def create_dpi_engine(logging_manager: LoggingManager, config_manager: ConfigManager, signatures_file: str) -> DPIEngineInterface:
    """Factory function to create and initialize the DPI engine and its modules."""
    return DPIEngine(logging_manager, config_manager, signatures_file) 