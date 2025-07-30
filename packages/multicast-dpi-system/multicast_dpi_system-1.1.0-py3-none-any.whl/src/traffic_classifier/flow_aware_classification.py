from typing import Dict, Optional
import time
from dataclasses import dataclass
from src.traffic_classifier.rule_classification import MulticastRuleBasedClassifier
from src.traffic_classifier.datamodels import ClassificationResult
from src.core.packet_context import PacketContext
from src.core.flow_stats_manager import FlowStatsManager, FlowStatistics
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.traffic_classifier.datamodels import PriorityLevel, BandwidthClass

@dataclass
class FlowBehavior:
    """Pure behavioral characteristics of a flow"""
    is_consistent: bool = False
    is_bursty: bool = False
    is_periodic: bool = False
    size_variation: float = 0.0
    rate_stability: float = 0.0
    jitter_level: float = 0.0

class FlowAwareClassifier:
    """
    Flow behavior analyzer that:
    1. Uses FlowStatsManager for raw metrics
    2. Focuses exclusively on behavioral patterns
    3. Complements rule-based classification
    """
    
    def __init__(self, 
                 logging_manager: LoggingManager,
                 config_manager: ConfigManager,
                 flow_stats_manager: FlowStatsManager):
        self.logger = logging_manager.get_logger("flow_analyzer")
        self.rule_classifier = MulticastRuleBasedClassifier(logging_manager, config_manager)
        self.flow_stats = flow_stats_manager
        self.behavior_cache: Dict[str, FlowBehavior] = {}
        
        # Behavioral analysis config
        self.config = config_manager.get_config('flow_analysis', {})
        self.maturity_threshold = self.config.get('maturity_threshold', 20)  # packets
        self.consistency_window = self.config.get('consistency_window', 10)  # packets
        self.jitter_threshold = self.config.get('jitter_threshold', 0.2)  # seconds
        self.category_rules = config_manager.get_config('category_rules', {})

    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        """Behavior-aware classification adjustment"""
        # Update flow statistics first
        stats = self.flow_stats.update_flow_stats(context)
        flow_key = self.flow_stats.get_flow_key(context)
        
        # Debug logging
        if stats is None:
            self.logger.warning(f"Flow statistics update returned None for flow_key: {flow_key}")
        else:
            self.logger.debug(f"Updated flow statistics for {flow_key}: packet_count={stats.packet_count}")
        
        # Get base classification from rule-based classifier
        base_result = self.rule_classifier.classify_traffic(context)
        
        # Set the category in flow statistics for display purposes
        if stats:
            stats.category = base_result.primary_category.value
        
        if not stats or stats.packet_count < self.maturity_threshold:
            return base_result
            
        # Analyze flow behavior
        behavior = self._analyze_flow_behavior(stats, flow_key)
        
        # Apply behavioral adjustments
        final_result = self._apply_behavioral_adjustments(base_result, behavior, stats)
        
        # Update the category in flow statistics with the final result
        if stats:
            stats.category = final_result.primary_category.value
        
        return final_result

    def _analyze_flow_behavior(self, stats: FlowStatistics, flow_key: str) -> FlowBehavior:
        """Extract behavioral patterns from flow statistics"""
        behavior = self.behavior_cache.get(flow_key, FlowBehavior())
        
        # Calculate rate stability (coefficient of variation)
        if stats.packet_count > 1 and stats.duration > 0:
            expected_pps = stats.packet_count / stats.duration
            behavior.rate_stability = min(1.0, stats.packets_per_second / expected_pps)
            
            # Jitter analysis (using last_seen updates)
            behavior.jitter_level = self._calculate_jitter(flow_key)
            
        # Size consistency
        if stats.packet_count > 0:
            behavior.size_variation = stats.average_packet_size / max(1, stats.byte_count)
            behavior.is_consistent = behavior.size_variation < 0.3
            
        # Update cache
        self.behavior_cache[flow_key] = behavior
        return behavior

    def _calculate_jitter(self, flow_key: str) -> float:
        """Calculate jitter based on packet timestamps"""
        stats = self.flow_stats.get_flow_statistics().get(flow_key)
        if stats and hasattr(stats, 'packet_timestamps'):
            # Calculate inter-arrival time variation
            iats = [t2-t1 for t1,t2 in zip(stats.packet_timestamps, stats.packet_timestamps[1:])]
            return max(iats) - min(iats) if iats else 0.0
        return 0.0

    def _apply_behavioral_adjustments(self, 
                                    base_result: ClassificationResult,
                                    behavior: FlowBehavior,
                                    stats: FlowStatistics) -> ClassificationResult:
        """Adjust classification based on flow behavior"""

        cat_rules = self.category_rules.get(base_result.primary_category.value, {})
        flow_params = cat_rules.get('flow_characteristics', {})
        new_confidence = base_result.confidence_score

        # Use the stats passed from classify_traffic instead of looking it up again
        if stats is None:
            self.logger.warning("Flow statistics is None in _apply_behavioral_adjustments")
            return base_result

        # Rate stability check
        if 'expected_pps' in flow_params and stats:
            min_pps, max_pps = flow_params['expected_pps']
            pps_ratio = min(1, stats.packets_per_second / max_pps) if stats.packets_per_second > max_pps else \
                       max(0, stats.packets_per_second / min_pps)
            new_confidence *= 0.5 + (0.5 * pps_ratio)  # Scale confidence based on PPS match

        # Burst tolerance adjustment
        if behavior.is_bursty and flow_params.get('burst_tolerance'):
            burst_factor = min(1.0, behavior.burst_level / flow_params['burst_tolerance'])
            new_confidence *= (1.0 - (0.3 * burst_factor))  # Up to 30% penalty for excessive bursts

        # Size variation check
        if flow_params.get('allow_size_variation', True) == False:
            if behavior.size_variation > 0.2:
                new_confidence *= 0.7

        # Special real-time handling
        if flow_params.get('latency_sensitive'):
            jitter_penalty = min(1.0, behavior.jitter_level / self.jitter_threshold)
            new_confidence *= (1.0 - (0.5 * jitter_penalty))

        
        # Confidence boosts for consistent flows
        if behavior.is_consistent:
            new_confidence = min(1.0, new_confidence * 1.2)
            
        # Penalize unstable flows
        if behavior.rate_stability < 0.7:
            new_confidence = max(0.1, new_confidence * 0.8)
                
        return ClassificationResult(
            primary_category=base_result.primary_category,
            sub_categories=base_result.sub_categories,
            priority_level=self._adjust_priority(base_result, behavior),
            bandwidth_class=self._adjust_bandwidth(base_result, behavior),
            confidence_score=max(0.1, min(1.0, new_confidence)),
            classification_metadata={
                **base_result.classification_metadata,
                'flow_analysis': {
                    'expected_vs_actual_pps': (flow_params.get('expected_pps'), stats.packets_per_second if stats else 0),
                    'burst_tolerance': flow_params.get('burst_tolerance'),
                    'size_variation': behavior.size_variation
                }
            },
            processing_time_ms=base_result.processing_time_ms
        )

    def _adjust_priority(self, result: ClassificationResult, behavior: FlowBehavior) -> PriorityLevel:
        """Adjust priority based on flow behavior"""
        if behavior.jitter_level > self.jitter_threshold and \
           result.primary_category in ["voice_call", "video_conference"]:
            return PriorityLevel(result.priority_level.value + 1)  # Increase priority
        return result.priority_level

    def _adjust_bandwidth(self, result: ClassificationResult, behavior: FlowBehavior) -> BandwidthClass:
        """Adjust bandwidth class based on flow patterns"""
        if behavior.is_bursty and result.bandwidth_class == BandwidthClass.MEDIUM:
            return BandwidthClass.HIGH
        return result.bandwidth_class

    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """Clean up old flow behaviors"""
        current_time = time.time()
        for flow_key, behavior in list(self.behavior_cache.items()):
            stats = self.flow_stats.get_flow_statistics().get(flow_key)
            if not stats or (current_time - stats.last_seen) > max_age_seconds:
                del self.behavior_cache[flow_key]