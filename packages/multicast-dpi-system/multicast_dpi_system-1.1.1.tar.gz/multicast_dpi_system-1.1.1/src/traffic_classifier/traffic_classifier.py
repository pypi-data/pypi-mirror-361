"""
Main Traffic Classifier Module

Integrates rule-based and flow-aware classifiers for comprehensive traffic classification.
"""
from typing import Dict, Any, Optional, List
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from src.core.flow_stats_manager import FlowStatistics
from src.interfaces.traffic_classifier import ITrafficClassifier
from .rule_classification import MulticastRuleBasedClassifier
# from .ml_classification import MLTrafficClassifier
from .datamodels import ClassificationResult
from .flow_aware_classification import FlowAwareClassifier
from collections import defaultdict
import time
from src.core.flow_stats_manager import FlowStatsManager
import yaml

class TrafficClassifier(ITrafficClassifier):
    """
    Main traffic classification engine for multicast DPI system.
    
    Combines rule-based and flow-aware classification approaches for optimal accuracy.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager, rules_file: str):
        self.logger = logging_manager.get_logger("traffic_classifier")
        self.json_logger = logging_manager.get_json_logger(self.__class__.__name__)
        self.config_manager = config_manager
        self.rules_file = rules_file
        self.flow_stats_manager = FlowStatsManager()
        self.classification_rules = self._load_rules_from_file(rules_file)
        self.rule_classifier = MulticastRuleBasedClassifier(logging_manager, config_manager)
        self.flow_aware_classifier = FlowAwareClassifier(
            logging_manager, 
            config_manager, 
            flow_stats_manager=self.flow_stats_manager
        )
        
        # Classification statistics
        self.stats = {
            'total_classified': 0,
            'rule_based_classifications': 0,
            'unknown_classifications': 0,
            'processing_time_total': 0.0
        }
        
        self.logger.info(f"TrafficClassifier initialized with rules file: {rules_file}")
        print(f"--- TrafficClassifier initialized with rules file: {rules_file}")
        
    
    def _load_rules_from_file(self, rules_file: str) -> dict:
        try:
            with open(rules_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load classification rules from {rules_file}: {e}")
            return {}
    
    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        """Classify traffic with enhanced metadata logging"""
        start_time = time.time()
        
        # Perform classification
        result = self.flow_aware_classifier.classify_traffic(context)
        
        # Extract relevant metadata
        flow_key = context.get_flow_key()
        stats = self.flow_stats_manager.get_flow_statistics().get(flow_key)
        
        # Debug logging for flow statistics
        if stats is None:
            self.logger.warning(f"No flow statistics found for flow_key: {flow_key}")
            self.logger.debug(f"Available flows: {list(self.flow_stats_manager.get_flow_statistics().keys())}")
        
        # Build enhanced log data with safe stats access
        if stats is not None:
            if stats.packet_count < 10:
                stage = "new"
            elif stats.packet_count < 50:
                stage = "established"
            else:
                stage = "mature"
            packet_count = stats.packet_count
            duration_sec = stats.duration
            avg_pps = stats.packets_per_second
        else:
            stage = "unknown"
            packet_count = 0
            duration_sec = 0
            avg_pps = 0
        
        log_data = {
            "packet_id": getattr(context, 'packet_id', None),
            "flow_id": flow_key,
            "classification": {
                "category": result.primary_category.value,
                "priority": result.priority_level.value,
                "bandwidth": result.bandwidth_class.value,
                "confidence": round(result.confidence_score, 2),
                "reason": result.classification_metadata.get('reason'),
                "flow_context": {
                    "stage": stage,
                    "packet_count": packet_count,
                    "duration_sec": duration_sec,
                    "avg_pps": avg_pps
                }
            },
            "processing_ms": round((time.time() - start_time) * 1000, 2)
        }
        
        # Add any additional flow analysis metadata
        if 'flow_analysis' in result.classification_metadata:
            log_data["classification"]["flow_analysis"] = {
                k: v for k, v in result.classification_metadata['flow_analysis'].items()
                if k not in ['sub_categories']  # Explicitly exclude
            }
        
        # Update context metadata (minimal version)
        context.classification_metadata = {
            'category': result.primary_category.value,
            'priority': result.priority_level.value,
            'flow_key': flow_key,
            'confidence': result.confidence_score
        }
        
        # JSON logging
        self.json_logger.log_json(log_data)
        
        # Update statistics
        self._update_stats(result, start_time)
        
        self.logger.debug(
            f"Classified {log_data['packet_id']} as {result.primary_category.value} "
            f"(confidence: {result.confidence_score:.2f}, "
            f"reason: {result.classification_metadata.get('reason', 'N/A')})"
        )
        
        return result
    
    def _update_flow_stats(self, context: PacketContext) -> None:
        """(Deprecated: handled by flow-aware classifier)"""
        pass
    
    def _flow_stats_to_dict(self, stats: Optional[FlowStatistics]) -> Optional[Dict[str, Any]]:
        """Convert FlowStatistics to dictionary for ML classifier"""
        if not stats:
            return None
        
        return {
            'avg_packet_size': stats.average_packet_size,
            'packet_size_std': 0.0,  # Would need packet history
            'duration': stats.duration,
            'packets_per_second': stats.packets_per_second,
            'bytes_per_second': stats.byte_count / stats.duration if stats.duration > 0 else 0
        }
    
    def _combine_results(self, rule_result: ClassificationResult, ml_result: Optional[ClassificationResult]) -> ClassificationResult:
        # ML classifier is disabled, always return rule_result
        self.stats['rule_based_classifications'] += 1
        return rule_result
    
    def _update_stats(self, result: ClassificationResult, start_time: float) -> None:
        """Update classification statistics"""
        self.stats['total_classified'] += 1
        processing_time = (time.time() - start_time) * 1000
        self.stats['processing_time_total'] += processing_time
        
        if result.primary_category.value == 'unknown':
            self.stats['unknown_classifications'] += 1
        else:
            self.stats['rule_based_classifications'] += 1
    
    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get comprehensive classification statistics"""
        total = self.stats['total_classified']
        avg_processing_time = (self.stats['processing_time_total'] / total) if total > 0 else 0
        
        return {
            'total_classified': total,
            'rule_based_percentage': (self.stats['rule_based_classifications'] / total * 100) if total > 0 else 0,
            'unknown_percentage': (self.stats['unknown_classifications'] / total * 100) if total > 0 else 0,
            'average_processing_time_ms': avg_processing_time,
            'active_flows': len(self.flow_stats_manager.get_flow_statistics()),
        }
    
    def get_flow_statistics(self) -> Dict[str, FlowStatistics]:
        """Get current flow statistics for monitoring"""
        return self.flow_stats_manager.get_flow_statistics()
    
    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """Clean up old flow statistics to prevent memory leaks"""
        self.flow_stats_manager.cleanup_old_flows(max_age_seconds)

    def shutdown(self) -> None:
        """Shutdown the traffic classifier and its submodules."""
        try:
            if hasattr(self.rule_classifier, 'shutdown'):
                self.rule_classifier.shutdown()
            if hasattr(self.flow_aware_classifier, 'shutdown'):
                self.flow_aware_classifier.shutdown()
            # If ML classifier is enabled in the future, add shutdown here
            self.logger.info("TrafficClassifier shutdown complete")
            print("\nTrafficClassifier shutdown complete")
            # Print statistics to terminal
            stats = self.get_classification_statistics()
            print("="*50)
            print("TRAFFIC CLASSIFICATION STATISTICS:")
            print("="*50)

            print(f"\n📊 Classification Summary:")
            print(f"   • Total classified: {stats['total_classified']}")
            print(f"   • Rule-based percentage: {stats['rule_based_percentage']:.1f}%")
            print(f"   • Unknown percentage: {stats['unknown_percentage']:.1f}%")
            print(f"   • Average processing time: {stats['average_processing_time_ms']:.2f} ms")
            print(f"   • Active flows: {stats['active_flows']}")

            print(f"\n🔍 Flow classifications:")
            for flow_key, flow_stats in self.get_flow_statistics().items():
                # Only print the flow key and the final category
                category = getattr(flow_stats, 'category', None)
                if not category and hasattr(flow_stats, 'classification_metadata'):
                    category = flow_stats.classification_metadata.get('category')
                if not category:
                    category = "unknown"
                print(f"  {flow_key}: {category}")
            print("\n")
            print("="*50)
        except Exception as e:
            self.logger.error(f"Error during TrafficClassifier shutdown: {e}")


# Factory function to create traffic classifier instance
def create_traffic_classifier(logging_manager: LoggingManager, config_manager: ConfigManager, rules_file: str) -> TrafficClassifier:
    """Factory function to create and initialize the traffic classifier with a rules file."""
    return TrafficClassifier(logging_manager, config_manager, rules_file)
