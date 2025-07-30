from typing import Dict, Any, List, Optional
import time
import ipaddress
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from .datamodels import TrafficCategory, PriorityLevel, BandwidthClass, ClassificationResult
from src.interfaces.traffic_classifier import ITrafficClassifier

class MulticastRuleBasedClassifier(ITrafficClassifier):
    """
    Multicast-optimized rule-based classifier with:
    - Special handling for multicast control protocols (IGMP, PIM)
    - Flexible protocol/codec matching
    - Stream-oriented classification
    - Size-tolerant confidence scoring
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager):
        self.logger = logging_manager.get_logger("multicast_rule_classifier")
        self.config_manager = config_manager
        self._category_rules = None
        self._custom_rules = None
        self._priority_rules = None
        self._bandwidth_rules = None
        self._protocol_families = {
            'RTP': ['RTP/AVP', 'RTP/SAVP', 'SRTP'],
            'RTSP': ['RTSP/1.0', 'RTSP/2.0'],
            'HTTP': ['HTTP/1.0', 'HTTP/1.1', 'HTTP/2', 'HTTP/3', 'HTTPS']
        }
        self._codec_variants = {
            'H264': ['H.264', 'AVC'],
            'H265': ['H.265', 'HEVC'],
            'AAC': ['AAC-LC', 'AAC-MC'],  # Added multicast variant
            'OPUS': ['OPUS-MC']
        }
        self.logger.info("MulticastRuleBasedClassifier initialized")

    @property
    def category_rules(self) -> Dict[TrafficCategory, Any]:
        if self._category_rules is None:
            self._category_rules = self._load_category_rules()
        return self._category_rules

    def _load_category_rules(self) -> Dict[TrafficCategory, Any]:
        """Load multicast-optimized category rules"""
        raw_rules = self.config_manager.get_config('category_rules', {})
        rules = {}
        
        for cat_str, config in raw_rules.items():
            try:
                category = TrafficCategory[cat_str.upper()]
                rules[category] = {
                    'protocols': [p.upper() for p in config.get('protocols', [])],
                    'codecs': [c.upper() for c in config.get('codecs', [])],
                    'packet_size_range': config.get('packet_size_range', [0, 1500]),
                    'flexible_matching': config.get('flexible_matching', True)
                }
            except KeyError:
                continue
                
        return rules

    def _enhanced_protocol_match(self, protocol: str, target_protocols: List[str]) -> bool:
        """Multicast-aware protocol matching"""
        protocol = protocol.upper().strip()
        
        # Special multicast protocols
        if protocol in ["IGMP", "MLD"]:
            return "MULTICAST_CONTROL" in target_protocols
        if protocol in ["PIM", "MSDP"]:
            return "MULTICAST_ROUTING" in target_protocols
            
        # Protocol family matching
        for family, variants in self._protocol_families.items():
            if family in target_protocols and protocol in variants:
                return True
                
        return protocol in target_protocols

    def _enhanced_codec_match(self, codec: str, target_codecs: List[str]) -> bool:
        """Codec matching with multicast variants"""
        codec = codec.upper().strip()
        
        # Check multicast variants first
        if '-MC' in codec and codec.replace('-MC', '') in target_codecs:
            return True
            
        # Standard variants
        for base_codec, variants in self._codec_variants.items():
            if base_codec in target_codecs and codec in variants:
                return True
                
        return codec in target_codecs

    def _calculate_size_confidence(self, size: int, size_range: List[int]) -> float:
        """Size confidence with multicast tolerance"""
        lower, upper = size_range
        if size < lower:
            return max(0.5, size / lower)  # Minimum 50% confidence for small packets
        if size > upper:
            return min(1.0, upper / size)  # Gradual decrease for large packets
        return 1.0

    def _determine_primary_category(self, context: PacketContext, dpi_results: Dict[str, Any]):
        """Multicast-optimized classification"""
        protocol_info = dpi_results.get('protocol_identification', {})
        protocol = protocol_info.get('application_protocol')
        protocol = protocol.upper() if protocol else ''
        codec = protocol_info.get('codec')
        codec = codec.upper() if codec else None
        packet_size = context.packet.length
        
        # 1. Check multicast control protocols first
        if protocol in ["IGMP", "MLD"]:
            return TrafficCategory.MULTICAST_CONTROL, {"protocol": protocol}, 1.0
        if protocol in ["PIM", "MSDP"]:
            return TrafficCategory.MULTICAST_ROUTING, {"protocol": protocol}, 1.0
            
        # 2. Proceed with normal classification
        best_category = TrafficCategory.UNKNOWN
        best_score = 0.0
        best_explanation = {}
        
        # Debug logging
        self.logger.debug(f"Classifying packet: protocol='{protocol}', codec='{codec}', size={packet_size}")
        
        for category, rules in self.category_rules.items():
            score = 0.0
            explanation = {}
            max_possible = 0
            
            # Protocol matching (50% weight) - HIGHEST PRIORITY
            if protocol and rules.get('protocols'):
                max_possible += 50
                if self._enhanced_protocol_match(protocol, rules['protocols']):
                    score += 50
                    explanation['protocol'] = protocol
                    self.logger.debug(f"  {category}: Protocol match '{protocol}' -> +50 points")
                    
            # Codec matching (30% weight) - SECOND PRIORITY
            if codec and rules.get('codecs'):
                max_possible += 30
                if self._enhanced_codec_match(codec, rules['codecs']):
                    score += 30
                    explanation['codec'] = codec
                    self.logger.debug(f"  {category}: Codec match '{codec}' -> +30 points")
                    
            # Packet size matching (20% weight) - LOWEST PRIORITY
            if rules.get('packet_size_range'):
                max_possible += 20
                size_conf = self._calculate_size_confidence(packet_size, rules['packet_size_range'])
                score += 20 * size_conf
                explanation['packet_size'] = {
                    'actual': packet_size,
                    'expected': rules['packet_size_range'],
                    'confidence': size_conf
                }
                self.logger.debug(f"  {category}: Size match {packet_size} in {rules['packet_size_range']} -> +{20 * size_conf:.1f} points")
                
            # Normalize and track best match
            if max_possible > 0:
                normalized_score = score / max_possible
                self.logger.debug(f"  {category}: Total score {score}/{max_possible} = {normalized_score:.2f}")
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_category = category
                    best_explanation = explanation
        
        self.logger.debug(f"Final classification: {best_category.value} (confidence: {best_score:.2f})")
        return best_category, best_explanation, best_score

    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        """Multicast-optimized classification entry point"""
        start_time = time.time()
        dpi_results = context.dpi_metadata or {}
        
        if not dpi_results:
            return self._create_unknown_result(context, start_time)
            
        # Special case: Very small packets with unknown protocol might be control messages
        # But ONLY if we don't have clear protocol/codec identification
        protocol_info = dpi_results.get('protocol_identification', {})
        protocol = protocol_info.get('application_protocol', '').upper()
        codec = protocol_info.get('codec', '').upper() if protocol_info.get('codec') else ''
        
        if context.packet.length < 64 and not protocol and not codec:
            return ClassificationResult(
                primary_category=TrafficCategory.MULTICAST_CONTROL,
                sub_categories=['multicast_control'],
                priority_level=PriorityLevel.CRITICAL,
                bandwidth_class=BandwidthClass.LOW,
                confidence_score=0.6,  # Lower confidence since we're guessing
                classification_metadata={
                    **self._build_metadata(context, dpi_results),
                    'reason': 'small_packet_no_protocol_identified',
                    'packet_size': context.packet.length
                },
                processing_time_ms=(time.time() - start_time) * 1000
            )
            
        # Normal classification
        primary_category, match_explanation, confidence = self._determine_primary_category(context, dpi_results)
        
        # Build reason from match explanation
        reason_parts = []
        if 'protocol' in match_explanation:
            reason_parts.append(f"protocol={match_explanation['protocol']}")
        if 'codec' in match_explanation:
            reason_parts.append(f"codec={match_explanation['codec']}")
        if 'packet_size' in match_explanation:
            reason_parts.append(f"size={match_explanation['packet_size']['actual']}")
        
        reason = " + ".join(reason_parts) if reason_parts else "rule_match"
        
        return ClassificationResult(
            primary_category=primary_category,
            sub_categories=self._determine_sub_categories(context, dpi_results, primary_category),
            priority_level=self._assign_priority(primary_category, dpi_results),
            bandwidth_class=self._classify_bandwidth(primary_category, dpi_results),
            confidence_score=confidence,
            classification_metadata={
                **self._build_metadata(context, dpi_results),
                'match_explanation': match_explanation,
                'reason': reason
            },
            processing_time_ms=(time.time() - start_time) * 1000
        )

    # Helper methods (similar to original but optimized for multicast)
    def _determine_sub_categories(self, context: PacketContext, dpi_results: Dict[str, Any], 
                                primary_category: TrafficCategory) -> List[str]:
        """Multicast-aware subcategories"""
        sub_cats = []
        proto_info = dpi_results.get('protocol_identification', {})
        
        # Protocol-based
        if proto_info.get('application_protocol'):
            proto = proto_info['application_protocol'].lower()
            sub_cats.append(f"proto_{proto}")
            
        # Codec-based
        if proto_info.get('codec'):
            codec = proto_info['codec'].lower()
            sub_cats.append(f"codec_{codec}")
            
        # Multicast-specific
        if primary_category in [TrafficCategory.MULTICAST_CONTROL, TrafficCategory.MULTICAST_ROUTING]:
            sub_cats.append("multicast_control")
            
        return list(set(sub_cats))

    def _assign_priority(self, category: TrafficCategory, dpi_results: Dict[str, Any]) -> PriorityLevel:
        """Priority assignment for multicast traffic"""
        if category == TrafficCategory.MULTICAST_CONTROL:
            return PriorityLevel.CRITICAL
        if category == TrafficCategory.MULTICAST_ROUTING:
            return PriorityLevel.HIGH
        return PriorityLevel.MEDIUM

    def _classify_bandwidth(self, category: TrafficCategory, dpi_results: Dict[str, Any]) -> BandwidthClass:
        """Bandwidth classification optimized for multicast"""
        if category in [TrafficCategory.VIDEO_STREAMING, TrafficCategory.IPTV]:
            return BandwidthClass.HIGH
        if category in [TrafficCategory.AUDIO_STREAMING, TrafficCategory.VOICE_CALL]:
            return BandwidthClass.MEDIUM
        return BandwidthClass.LOW

    def _build_metadata(self, context: PacketContext, dpi_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced metadata for multicast"""
        return {
            'flow_key': context.get_flow_key(),
            'dpi_results': dpi_results,
            'packet_length': context.packet.length,
            'timestamp': context.packet.timestamp,
            'multicast_destination': context.packet.dst_ip
        }

    def _create_unknown_result(self, context: PacketContext, start_time: float) -> ClassificationResult:
        """Unknown result handler"""
        return ClassificationResult(
            primary_category=TrafficCategory.UNKNOWN,
            sub_categories=['unclassified'],
            priority_level=PriorityLevel.LOW,
            bandwidth_class=BandwidthClass.LOW,
            confidence_score=0.0,
            classification_metadata={
                'flow_key': context.get_flow_key(),
                'reason': 'no_dpi_results',
                'multicast_destination': context.packet.dst_ip
            },
            processing_time_ms=(time.time() - start_time) * 1000
        )

    def get_classification_statistics(self) -> Dict[str, Any]:
        """Statistics reporting"""
        return {'method': 'multicast_rule_based'}

    def get_flow_statistics(self) -> Dict[str, Any]:
        """Flow statistics (not used in rule-based)"""
        return {}

    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """Flow cleanup (not used in rule-based)"""
        pass