"""
Protocol Identifier Module - Specialized for Application Protocols

This module identifies application-level protocols with minimal overhead:
- Port-based lookup for common services
- Payload pattern matching for application protocols
- Codec detection for media traffic
- NO encryption detection (handled by encrypted_analyzer)
"""
import re
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from src.core.packet import Packet
from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager
from collections import Counter
from src.utils.config_handler import ConfigManager


@dataclass
class ProtocolInfo:
    """Application protocol identification results"""
    transport_protocol: str
    application_protocol: Optional[str] = None
    confidence: float = 0.0
    codec: Optional[str] = None
    detection_method: str = "none"


class ProtocolIdentifier:
    """
    Specialized identifier for application-level protocols.
    
    This module focuses on identifying application protocols (HTTP, FTP, DNS, etc.)
    and media codecs. Encryption detection is handled by the encrypted_analyzer.
    """
    
    def __init__(self, logging_manager: LoggingManager, config: Dict[str, Any]):
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.config = config or {}
        self.stats = {'protocols_identified': Counter(), 'codecs_identified': Counter()}
        
        # Well-known port → application mapping (common services)
        self.port_map = {
            80: "HTTP", 5060: "SIP", 5004: "RTP", 5005: "RTCP",
            21: "FTP", 25: "SMTP", 53: "DNS", 110: "POP3", 
            143: "IMAP", 587: "SMTP_SUBMISSION", 993: "IMAPS",
            995: "POP3S", 22: "SSH", 23: "TELNET", 69: "TFTP",
            123: "NTP", 161: "SNMP", 389: "LDAP", 636: "LDAPS"
        }
        
        # Application protocol patterns (non-encrypted)
        self.patterns = {
            "HTTP": re.compile(rb"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|TRACE|CONNECT) .+ HTTP/\d\.\d"),
            "SIP":  re.compile(rb"^(INVITE|ACK|BYE|CANCEL|REGISTER|OPTIONS|INFO|PRACK|UPDATE|SUBSCRIBE|NOTIFY|REFER|MESSAGE|PUBLISH) .+ SIP/\d\.\d"),
            "RTP":  re.compile(rb"^[\x80-\xbf]"),
            "FTP":  re.compile(rb"^(USER|PASS|ACCT|CWD|CDUP|QUIT|REIN|PORT|PASV|TYPE|STRU|MODE|RETR|STOR|STOU|APPE|ALLO|REST|RNFR|RNTO|ABOR|DELE|RMD|MKD|PWD|LIST|NLST|SITE|SYST|STAT|HELP|NOOP)"),
            "SMTP": re.compile(rb"^(HELO|EHLO|MAIL|RCPT|DATA|RSET|VRFY|EXPN|HELP|NOOP|QUIT)"),
            "DNS":  re.compile(rb"^[\x00-\x0f]"),  # DNS query/response header
            "POP3": re.compile(rb"^(USER|PASS|APOP|STAT|LIST|RETR|DELE|NOOP|RSET|QUIT|TOP|UIDL)"),
            "IMAP": re.compile(rb"^(LOGIN|AUTHENTICATE|SELECT|EXAMINE|CREATE|DELETE|RENAME|SUBSCRIBE|UNSUBSCRIBE|LIST|LSUB|STATUS|APPEND|CLOSE|EXPUNGE|SEARCH|FETCH|STORE|COPY|UID|CAPABILITY|NOOP|LOGOUT)"),
            "TELNET": re.compile(rb"^(USER|PASS|LOGIN|LOGOUT)"),
            "SNMP": re.compile(rb"^\x30"),  # SNMP BER encoding starts with 0x30
            "NTP": re.compile(rb"^[\x1b\x23\x27\x2b\xdb\xdf\xe3\xe7]")  # NTP version/stratum
        }
        
        # Enhanced codec detection patterns
        self.codec_patterns = {
            # Video codecs
            "H264": [
                re.compile(rb"H\.264|h264|avc1|H264", re.IGNORECASE),
                re.compile(rb"profile-level-id=", re.IGNORECASE),  # SDP H.264
                re.compile(rb"packetization-mode=", re.IGNORECASE),  # SDP H.264
            ],
            "H265": [
                re.compile(rb"H\.265|h265|hevc|H265", re.IGNORECASE),
                re.compile(rb"profile-id=", re.IGNORECASE),  # SDP H.265
            ],
            "VP8": [
                re.compile(rb"VP8|vp8", re.IGNORECASE),
                re.compile(rb"max-fr=", re.IGNORECASE),  # SDP VP8
            ],
            "VP9": [
                re.compile(rb"VP9|vp9", re.IGNORECASE),
                re.compile(rb"profile-id=", re.IGNORECASE),  # SDP VP9
            ],
            "AV1": [
                re.compile(rb"AV1|av1", re.IGNORECASE),
            ],
            
            # Audio codecs
            "OPUS": [
                re.compile(rb"OPUS|opus", re.IGNORECASE),
                re.compile(rb"maxplaybackrate=", re.IGNORECASE),  # SDP Opus
            ],
            "AAC": [
                re.compile(rb"AAC|aac", re.IGNORECASE),
                re.compile(rb"profile-level-id=", re.IGNORECASE),  # SDP AAC
            ],
            "MP3": [
                re.compile(rb"MP3|mp3", re.IGNORECASE),
            ],
            "PCM": [
                re.compile(rb"PCM|pcm", re.IGNORECASE),
                re.compile(rb"L8|L16|L24", re.IGNORECASE),  # SDP PCM
            ],
            "G711": [
                re.compile(rb"PCMA|PCMU|G711", re.IGNORECASE),
            ],
            "G722": [
                re.compile(rb"G722", re.IGNORECASE),
            ],
            "G729": [
                re.compile(rb"G729", re.IGNORECASE),
            ],
            
            # Container formats
            "MP4": [
                re.compile(rb"ftypmp4|ftypiso|ftypM4V", re.IGNORECASE),
            ],
            "WEBM": [
                re.compile(rb"ftypwebm", re.IGNORECASE),
            ],
            "FLV": [
                re.compile(rb"FLV", re.IGNORECASE),
            ],
        }
        
        # Binary codec signatures (magic bytes)
        self.codec_signatures = {
            "H264": [b"\x00\x00\x00\x01", b"\x00\x00\x01", b"\x80"],  # NAL start codes
            "H265": [b"\x00\x00\x00\x01", b"\x00\x00\x01", b"\x80"],  # NAL start codes
            "MP3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],  # MP3 headers
            "AAC": [b"\xff\xf1", b"\xff\xf9"],  # AAC ADTS headers
            "FLAC": [b"fLaC"],  # FLAC signature
            "WAV": [b"RIFF"],  # WAV signature
            "MP4": [b"ftyp"],  # MP4 signature
            "WEBM": [b"ftyp"],  # WebM signature
        }
    
    def identify_protocol(self, context: PacketContext) -> None:
        """
        Analyze packet and add application protocol identification metadata to the context.
        
        This module focuses on application-level protocols and does NOT detect encryption.
        Encryption detection is handled by the encrypted_analyzer module.
        """
        try:
            context.mark_entry('protocol_identifier')
            packet = context.packet
            protocol_info = self._analyze_packet(packet)
            context.dpi_metadata['protocol_identification'] = asdict(protocol_info)
            context.mark_exit('protocol_identifier')
        except Exception as e:
            self.logger.error(f"Error in protocol identification: {e}")
            context.add_error('protocol_identifier', str(e))

    def _analyze_packet(self, packet: Packet) -> ProtocolInfo:
        """
        Analyze packet to identify application-level protocols and codecs.
        Enhanced codec detection works regardless of protocol.
        """
        info = ProtocolInfo(transport_protocol=packet.protocol or "Unknown")
        
        # Get payload for analysis
        payload = packet.payload or b""
        
        # PRIORITY 1: Codec detection (highest priority - works regardless of protocol)
        detected_codec = self._detect_codec(payload)
        if detected_codec:
            info.codec = detected_codec
            info.confidence = max(info.confidence, 0.9)
            info.detection_method = "payload_analysis"
        
        # PRIORITY 2: Port-based lookup for application protocols
        if packet.dst_port in self.port_map:
            info.application_protocol = self.port_map[packet.dst_port]
            info.confidence = max(info.confidence, 0.8)
            if info.detection_method == "none":
                info.detection_method = "port"
        
        # PRIORITY 3: Pattern-based detection for application protocols
        for proto, pattern in self.patterns.items():
            if pattern.search(payload):
                info.application_protocol = proto
                info.confidence = max(info.confidence, 0.9)
                if info.detection_method == "none":
                    info.detection_method = "pattern"
                break
        
        # PRIORITY 4: Special handling for encrypted protocols (basic identification only)
        # Note: Detailed encryption analysis is done by encrypted_analyzer
        if packet.dst_port == 443:
            info.application_protocol = "HTTPS"
            info.confidence = max(info.confidence, 0.9)
            if info.detection_method == "none":
                info.detection_method = "port"
        elif packet.dst_port == 993:
            info.application_protocol = "IMAPS"
            info.confidence = max(info.confidence, 0.9)
            if info.detection_method == "none":
                info.detection_method = "port"
        elif packet.dst_port == 995:
            info.application_protocol = "POP3S"
            info.confidence = max(info.confidence, 0.9)
            if info.detection_method == "none":
                info.detection_method = "port"
        
        return info

    def _detect_codec(self, payload: bytes) -> Optional[str]:
        """
        Enhanced codec detection that works regardless of protocol.
        Uses multiple detection methods for maximum accuracy.
        """
        if not payload:
            return None
        
        # Method 1: Binary signature detection (most reliable for binary data)
        for codec, signatures in self.codec_signatures.items():
            for signature in signatures:
                if payload.startswith(signature):
                    return codec
        
        # Method 2: Pattern-based detection (for text-based protocols like SDP)
        for codec, patterns in self.codec_patterns.items():
            for pattern in patterns:
                if pattern.search(payload):
                    return codec
        
        # Method 3: SDP-specific codec detection
        sdp_codec = self._detect_sdp_codec(payload)
        if sdp_codec:
            return sdp_codec
        
        # Method 4: RTP payload type detection
        rtp_codec = self._detect_rtp_codec(payload)
        if rtp_codec:
            return rtp_codec
        
        return None

    def _detect_sdp_codec(self, payload: bytes) -> Optional[str]:
        """Detect codec from SDP (Session Description Protocol) data"""
        try:
            payload_str = payload.decode('utf-8', errors='ignore')
            
            # Common SDP codec mappings
            sdp_codec_map = {
                'H264': ['H264', 'h264', 'avc1'],
                'H265': ['H265', 'h265', 'hevc'],
                'VP8': ['VP8', 'vp8'],
                'VP9': ['VP9', 'vp9'],
                'OPUS': ['opus', 'OPUS'],
                'AAC': ['aac', 'AAC', 'mpeg4-generic'],
                'PCM': ['L8', 'L16', 'L24'],
                'G711': ['PCMA', 'PCMU'],
                'G722': ['G722'],
                'G729': ['G729'],
            }
            
            for codec, patterns in sdp_codec_map.items():
                for pattern in patterns:
                    if pattern in payload_str:
                        return codec
                        
        except (UnicodeDecodeError, AttributeError):
            pass
        
        return None

    def _detect_rtp_codec(self, payload: bytes) -> Optional[str]:
        """Detect codec from RTP payload type"""
        if len(payload) < 12:  # RTP header is 12 bytes
            return None
        
        try:
            # RTP payload type is in the second byte, bits 0-6
            payload_type = payload[1] & 0x7F
            
            # Comprehensive RTP payload type mappings
            rtp_codec_map = {
                # Standard audio codecs
                0: "PCMU",     # G.711 u-law
                3: "GSM",      # GSM
                4: "G723",     # G.723.1
                5: "DVI4",     # DVI4 8kHz
                6: "DVI4",     # DVI4 16kHz
                7: "LPC",      # LPC
                8: "PCMA",     # G.711 a-law
                9: "G722",     # G.722
                10: "L16",     # L16 10kHz
                11: "L16",     # L16 8kHz
                12: "QCELP",   # QCELP
                13: "CN",      # Comfort Noise
                14: "MPA",     # MPEG Audio
                15: "G728",    # G.728
                16: "DVI4",    # DVI4 11kHz
                17: "DVI4",    # DVI4 22kHz
                18: "G729",    # G.729
                25: "CELB",    # CELB
                26: "JPEG",    # JPEG
                28: "NV",      # NV
                31: "H261",    # H.261
                32: "MPV",     # MPEG Video
                33: "MP2T",    # MPEG2 Transport
                34: "H263",    # H.263
                
                # Dynamic payload types (commonly used)
                96: "H264",    # H.264 (dynamic)
                97: "H265",    # H.265/HEVC (dynamic)
                98: "VP8",     # VP8 (dynamic)
                99: "VP9",     # VP9 (dynamic)
                100: "OPUS",   # Opus (dynamic)
                101: "AAC",    # AAC (dynamic)
                102: "H264",   # H.264 (alternative)
                103: "H265",   # H.265 (alternative)
                104: "VP8",    # VP8 (alternative)
                105: "VP9",    # VP9 (alternative)
                106: "OPUS",   # Opus (alternative)
                107: "AAC",    # AAC (alternative)
                108: "H264",   # H.264 (another alternative)
                109: "H265",   # H.265 (another alternative)
                110: "VP8",    # VP8 (another alternative)
                111: "VP9",    # VP9 (another alternative)
                112: "OPUS",   # Opus (another alternative)
                113: "AAC",    # AAC (another alternative)
                
                # Additional common dynamic types
                114: "H264",   # H.264
                115: "H265",   # H.265
                116: "VP8",    # VP8
                117: "VP9",    # VP9
                118: "OPUS",   # Opus
                119: "AAC",    # AAC
                120: "H264",   # H.264
                121: "H265",   # H.265
                122: "VP8",    # VP8
                123: "VP9",    # VP9
                124: "OPUS",   # Opus
                125: "AAC",    # AAC
                126: "H264",   # H.264
                127: "H265",   # H.265
            }
            
            if payload_type in rtp_codec_map:
                return rtp_codec_map[payload_type]
            else:
                # For unknown payload types, try to detect from payload content
                return self._detect_codec_from_rtp_payload(payload)
            
        except (IndexError, TypeError):
            pass
        
        return None

    def _detect_codec_from_rtp_payload(self, payload: bytes) -> Optional[str]:
        """Try to detect codec from RTP payload content when payload type is unknown"""
        if len(payload) < 12:
            return None
        
        # Skip RTP header (12 bytes) and analyze payload
        rtp_payload = payload[12:]
        
        # Check for H.264 NAL start codes
        if rtp_payload.startswith(b"\x00\x00\x00\x01") or rtp_payload.startswith(b"\x00\x00\x01"):
            return "H264"
        
        # Check for H.265 NAL start codes (same as H.264 but different NAL type)
        if len(rtp_payload) > 4:
            nal_header = rtp_payload[4] if rtp_payload.startswith(b"\x00\x00\x00\x01") else rtp_payload[3]
            if (nal_header >> 1) & 0x3F in [32, 33, 34]:  # H.265 NAL types
                return "H265"
        
        # Check for VP8/VP9 patterns
        if b"VP8" in rtp_payload or b"vp8" in rtp_payload:
            return "VP8"
        
        if b"VP9" in rtp_payload or b"vp9" in rtp_payload:
            return "VP9"
        
        # Check for Opus patterns
        if b"OPUS" in rtp_payload or b"opus" in rtp_payload:
            return "OPUS"
        
        # Check for AAC patterns
        if b"AAC" in rtp_payload or b"aac" in rtp_payload:
            return "AAC"
        
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get protocol identification statistics"""
        return {
            'protocols_identified': len(self.port_map),
            'patterns_available': len(self.patterns),
            'codecs_supported': len(self.codec_patterns),
            'binary_signatures': len(self.codec_signatures)
        }

    def shutdown(self):
        """Graceful shutdown."""
        pass


def create_protocol_identifier(logging_manager: LoggingManager, config: Dict[str, Any]) -> ProtocolIdentifier:
    """Factory function for ProtocolIdentifier."""
    return ProtocolIdentifier(logging_manager, config)
