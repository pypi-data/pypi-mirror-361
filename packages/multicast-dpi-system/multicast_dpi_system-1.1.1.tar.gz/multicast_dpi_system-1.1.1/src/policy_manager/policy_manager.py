"""
Policy Manager Module

Coordinates policy definition, enforcement, monitoring, and integration
with other system modules in the Multicast DPI System.
"""
import threading
import time
from typing import Dict, Any, List, Optional
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from src.core.flow_stats_manager import FlowStatsManager
from src.interfaces.policy_manager.policy_manager import IPolicyManager
from src.interfaces.policy_manager.policy_engine import IPolicyEngine
from src.interfaces.policy_manager.policy_config import IPolicyConfig
from src.policy_manager.policy_engine import PolicyEngine
from src.policy_manager.policy_config import PolicyConfigManager
from src.policy_manager.policy_models import PolicyRule, PolicyStatistics, PolicyEnforcementResult

class PolicyManager(IPolicyManager):
    """
    Main Policy Manager for the multicast DPI system.
    Applies and manages policies per flow, with dynamic re-evaluation based on flow statistics.
    """
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager,
                 policy_engine: Optional[IPolicyEngine] = None,
                 policy_config: Optional[IPolicyConfig] = None):
        # Logging
        self.logger = logging_manager.get_logger("system")  # Info/debug logs to system.log
        self.json_logger = logging_manager.get_json_logger("policy_manager")  # Per-packet logs only
        # Config
        self.config_manager = config_manager
        # Core components (dependency injection)
        self.policy_engine = policy_engine or PolicyEngine(logging_manager, config_manager)
        self.policy_config = policy_config or PolicyConfigManager(logging_manager, config_manager)
        # Flow statistics (centralized)
        self.flow_stats_manager = FlowStatsManager()
        # Per-flow policy cache: flow_key -> {'policy_metadata': ..., 'last_stats': ...}
        self.flow_policy_map: Dict[str, Dict[str, Any]] = {}
        # Enforcement tracking
        self.enforcement_stats = {
            'packets_processed': 0,
            'policies_matched': 0,
            'actions_executed': 0,
            'processing_errors': 0,
            'unique_flows_processed': 0,
            'policy_cache_size': 0
        }
        # Lifecycle
        self.cleanup_thread = None
        self.running = False
        self._start_time = time.time()
        self.logger.info("PolicyManager initialized")
        print(f"--- PolicyManager initialized")

    def start(self) -> bool:
        """Start the policy manager and background services."""
        try:
            self.running = True
            self._start_time = time.time()
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                name="PolicyCleanup",
                daemon=True
            )
            self.cleanup_thread.start()
            self.logger.info("PolicyManager started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start PolicyManager: {e}")
            return False

    def stop(self) -> None:
        """Stop the policy manager and cleanup resources."""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        self.logger.info("PolicyManager stopped")
        print(f"🛑 PolicyManager stopped")

    def process_packet(self, context: PacketContext) -> List[PolicyEnforcementResult]:
        """
        Process a packet through the policy engine with dynamic per-flow logic.
        - On first packet of a flow: evaluate and cache policy.
        - On subsequent packets: re-evaluate policy if flow stats change significantly.
        - Always apply the cached policy to the packet.
        """
        try:
            # Increment packets processed counter
            self.enforcement_stats['packets_processed'] += 1
            
            context.mark_entry('policy')
            flow_key = context.get_flow_key()
            # Update flow stats centrally
            flow_stats = self.flow_stats_manager.update_flow_stats(context)
            stats_snapshot = self._extract_flow_stats_snapshot(flow_stats)
            policy_entry = self.flow_policy_map.get(flow_key)
            reeval_needed = False
            enforcement_results = []
            
            if policy_entry is None:
                # First packet of flow: evaluate and cache policy
                enforcement_results = self.policy_engine.evaluate_policies(context)
                # Increment policies matched counter
                if enforcement_results:
                    self.enforcement_stats['policies_matched'] += 1
                    self.enforcement_stats['actions_executed'] += len(enforcement_results)
                
                self.flow_policy_map[flow_key] = {
                    'policy_metadata': context.policy_metadata.copy(),
                    'last_stats': stats_snapshot.copy()
                }
                # Track unique flows and cache size
                self.enforcement_stats['unique_flows_processed'] += 1
                self.enforcement_stats['policy_cache_size'] = len(self.flow_policy_map)
                
                # Per-packet JSON log - always log when policy is evaluated
                log_data = {
                    "packet_id": getattr(context, 'packet_id', None),
                    "flow_id": flow_key,
                    "policy_metadata": context.policy_metadata,
                    "event": "policy_evaluated"
                }
                self.json_logger.log_json(log_data)
            else:
                # Check if flow stats have changed enough to require re-evaluation
                last_stats = policy_entry['last_stats']
                # Re-evaluate if packets_per_second, duration, or average_packet_size changes significantly
                if (
                    abs(stats_snapshot['packets_per_second'] - last_stats['packets_per_second']) > 10 or
                    abs(stats_snapshot['duration'] - last_stats['duration']) > 5 or
                    abs(stats_snapshot['average_packet_size'] - last_stats['average_packet_size']) > 100
                ):
                    reeval_needed = True
                if reeval_needed:
                    enforcement_results = self.policy_engine.evaluate_policies(context)
                    # Increment policies matched counter for re-evaluation
                    if enforcement_results:
                        self.enforcement_stats['policies_matched'] += 1
                        self.enforcement_stats['actions_executed'] += len(enforcement_results)
                    
                    # If the policy changed, update the cache and log
                    if context.policy_metadata != policy_entry['policy_metadata']:
                        self.flow_policy_map[flow_key] = {
                            'policy_metadata': context.policy_metadata.copy(),
                            'last_stats': stats_snapshot.copy()
                        }
                        log_data = {
                            "packet_id": getattr(context, 'packet_id', None),
                            "flow_id": flow_key,
                            "policy_metadata": context.policy_metadata,
                            "event": "policy_updated"
                        }
                        self.json_logger.log_json(log_data)
                    else:
                        # Just update stats
                        policy_entry['last_stats'] = stats_snapshot.copy()
                else:
                    # Apply cached policy - still count as action executed
                    if policy_entry['policy_metadata']:
                        self.enforcement_stats['actions_executed'] += 1
                    
                    # Log cached policy application (less frequently)
                    if self.enforcement_stats['packets_processed'] % 100 == 0:  # Log every 100th packet
                        log_data = {
                            "packet_id": getattr(context, 'packet_id', None),
                            "flow_id": flow_key,
                            "policy_metadata": policy_entry['policy_metadata'],
                            "event": "cached_policy_applied"
                        }
                        self.json_logger.log_json(log_data)
                
                # Always apply cached policy to this packet
                context.policy_metadata = policy_entry['policy_metadata'].copy()
            
            context.mark_exit('policy')
            return enforcement_results
            
        except Exception as e:
            self.enforcement_stats['processing_errors'] += 1
            self.logger.error(f"Packet processing failed: {e}")
            context.add_error('policy', str(e))
            return []

    def add_policy(self, policy: PolicyRule) -> bool:
        """Add a new policy to the manager."""
        return self.policy_engine.add_policy(policy)

    def remove_policy(self, rule_id: str) -> bool:
        """Remove a policy from the manager."""
        return self.policy_engine.remove_policy(rule_id)

    def get_active_policies(self) -> List[PolicyRule]:
        """Get all active policies."""
        return self.policy_engine.get_active_policies()

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive policy manager statistics."""
        engine_stats = self.policy_engine.get_statistics()
        
        # Ensure cache size is current
        self.enforcement_stats['policy_cache_size'] = len(self.flow_policy_map)
        
        return {
            'enforcement': self.enforcement_stats.copy(),
            'engine': {
                'total_policies': engine_stats.total_policies,
                'active_policies': engine_stats.active_policies,
                'total_matches': engine_stats.total_matches,
                'total_enforcements': engine_stats.total_enforcements,
                'success_rate': engine_stats.enforcement_success_rate,
                'avg_processing_time_ms': engine_stats.average_processing_time_ms
            },
            'system': {
                'running': self.running,
                'uptime_seconds': time.time() - self._start_time
            }
        }

    def create_policy_from_template(self, template_category: str, template_name: str,
                                  custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create and add a policy from a template."""
        policy = self.policy_config.create_policy_from_template(
            template_category, template_name, custom_parameters
        )
        if policy and self.add_policy(policy):
            return policy.rule_id
        return None

    def export_configuration(self, export_path: str) -> bool:
        """Export current policy configuration."""
        active_policies = self.get_active_policies()
        return self.policy_config.export_policies_to_file(active_policies, export_path)

    def _cleanup_worker(self) -> None:
        """Background worker for policy cleanup and maintenance."""
        cleanup_interval = self.config_manager.get_config('policy_manager', {}).get('cleanup_interval_minutes', 60)
        while self.running:
            try:
                time.sleep(cleanup_interval * 60)
                if not self.running:
                    break
                expired_count = self.policy_engine.cleanup_expired_policies()
                if expired_count > 0:
                    self.logger.info(f"Cleanup completed: {expired_count} expired policies removed")
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")

    def shutdown(self) -> None:
        """Shutdown the policy manager and print statistics."""
        try:
            self.stop()
            stats = self.get_statistics()
            print("="*50)
            print("POLICY MANAGER STATISTICS:")
            print("="*50)
            print(f"\n📊 Enforcement stats:")
            print(f"   - Packets processed: {stats['enforcement']['packets_processed']}")
            print(f"   - Policies matched: {stats['enforcement']['policies_matched']}")
            print(f"   - Actions executed: {stats['enforcement']['actions_executed']}")
            print(f"   - Processing errors: {stats['enforcement']['processing_errors']}")
            print(f"   - Unique flows processed: {stats['enforcement']['unique_flows_processed']}")
            print(f"   - Policy cache size: {stats['enforcement']['policy_cache_size']}")
            print(f"\n⏱️ System uptime: {stats['system']['uptime_seconds']:.2f} seconds")
            print("\n")
            print("="*50)
        except Exception as e:
            self.logger.error(f"Error during PolicyManager shutdown: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def _extract_flow_stats_snapshot(self, flow_stats):
        """Extract a snapshot of relevant flow statistics for policy decisions."""
        return {
            'bandwidth_class': getattr(flow_stats, 'bandwidth_class', None),
            'packet_count': flow_stats.packet_count,
            'byte_count': flow_stats.byte_count,
            'duration': flow_stats.duration,
            'packets_per_second': flow_stats.packets_per_second,
            'average_packet_size': flow_stats.average_packet_size,
        }
