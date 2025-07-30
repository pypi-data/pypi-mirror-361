"""
Encrypted Traffic Analyzer Module - Lightweight Version

This module provides minimal encryption detection with essential metadata only:
- Basic TLS/SSL detection
- Simple entropy calculation
- Minimal metadata storage
"""
import math
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from src.core.packet import Packet
from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager


@dataclass
class EncryptionInfo:
    """Minimal encryption detection results"""
    is_encrypted: bool = False
    encryption_type: Optional[str] = None
    entropy_score: float = 0.0


class EncryptedAnalyzer:
    """
    Lightweight analyzer for basic encryption detection.
    
    Stores only essential metadata needed for encryption identification.
    """
    
    def __init__(self, logging_manager: LoggingManager, config: Dict[str, Any]):
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.config = config or {}
        self.entropy_threshold = self.config.get('entropy_threshold', 7.5)
        self.stats = {'encrypted_detected': 0, 'decrypted_detected': 0}
    
    def analyze_encryption(self, context: PacketContext) -> None:
        """
        Analyze packet for basic encryption characteristics.
        
        Stores only essential metadata needed for encryption detection.
        """
        try:
            context.mark_entry('encrypted_analyzer')
            packet = context.packet
            encryption_info = self._analyze_packet(packet)
            context.dpi_metadata['encryption_analysis'] = asdict(encryption_info)
            context.mark_exit('encrypted_analyzer')
        except Exception as e:
            self.logger.error(f"Error in encryption analysis: {e}")
            context.add_error('encrypted_analyzer', str(e))

    def _analyze_packet(self, packet: Packet) -> EncryptionInfo:
        """
        Analyze packet for basic encryption characteristics.
        Stores only essential metadata.
        """
        info = EncryptionInfo()
        
        # Get payload for analysis
        payload = packet.payload or b""
        
        if not payload:
            return info
        
        # 1. Basic TLS/SSL detection
        if self._is_tls_ssl(payload):
            info.is_encrypted = True
            info.encryption_type = "TLS/SSL"
        
        # 2. Basic SSH detection
        elif payload.startswith(b"SSH-"):
            info.is_encrypted = True
            info.encryption_type = "SSH"
        
        # 3. Entropy-based detection (fallback)
        else:
            entropy = self._calculate_entropy(payload)
            info.entropy_score = entropy
            
            if entropy > self.entropy_threshold:
                info.is_encrypted = True
                info.encryption_type = "Unknown_Encrypted"
        
        return info

    def _is_tls_ssl(self, payload: bytes) -> bool:
        """Basic TLS/SSL handshake detection"""
        if len(payload) < 5:
            return False
        
        # TLS handshake: first byte 0x16 and version >= 0x0300
        return payload[0] == 0x16 and payload[1] == 0x03

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate basic Shannon entropy"""
        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * math.log2(probability)
        
        return entropy

    def get_stats(self) -> dict:
        """Get basic statistics"""
        return {
            'entropy_threshold': self.entropy_threshold
        }

    def shutdown(self):
        """Graceful shutdown."""
        pass

def create_encrypted_analyzer(logging_manager: LoggingManager, config: Dict[str, Any]) -> EncryptedAnalyzer:
    """Factory function for EncryptedAnalyzer."""
    return EncryptedAnalyzer(logging_manager, config)
