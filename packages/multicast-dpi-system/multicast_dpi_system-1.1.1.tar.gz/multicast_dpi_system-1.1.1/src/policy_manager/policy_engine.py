"""
Core Policy Engine for Multicast DPI System

Handles policy evaluation, enforcement, and conflict resolution with
real-time processing capabilities.
"""
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from src.interfaces.policy_manager.policy_engine import IPolicyEngine
from src.policy_manager.policy_models import PolicyRule, PolicyCondition, PolicyAction, PolicyEnforcementResult, PolicyStatistics, PolicyStatus, PolicyPriority

class PolicyEngine(IPolicyEngine):
    """
    Core policy engine for real-time policy evaluation and enforcement.
    
    Provides fast policy matching, conflict resolution, and enforcement
    action execution for multicast DPI traffic analysis.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager):
        self.logger = logging_manager.get_logger("policy_engine")
        self.json_logger = logging_manager.get_json_logger(self.__class__.__name__)
        self.config_manager = config_manager
        
        # Policy storage and indexing
        self.policies: Dict[str, PolicyRule] = {}
        self.policy_index: Dict[str, List[str]] = defaultdict(list)  # field -> rule_ids
        
        # Enforcement tracking
        self.enforcement_history = deque(maxlen=10000)
        self.policy_stats = PolicyStatistics()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance optimization
        self._condition_cache: Dict[str, bool] = {}
        self._cache_max_size = self.config_manager.get_config('policy_engine', {}).get('cache_size', 1000)
        
        # Load default policies
        self._load_default_policies()
        
        self.logger.info("PolicyEngine initialized")
    
    def add_policy(self, policy: PolicyRule) -> bool:
        """
        Add a new policy rule to the engine.
        
        Args:
            policy: PolicyRule to add
            
        Returns:
            bool: True if policy was added successfully
        """
        try:
            with self._lock:
                # Validate policy
                if not self._validate_policy(policy):
                    self.logger.error(f"Invalid policy: {policy.name}")
                    return False
                
                # Store policy
                self.policies[policy.rule_id] = policy
                
                # Update index for fast lookups
                self._update_policy_index(policy)
                
                # Update statistics
                self.policy_stats.total_policies = len(self.policies)
                self.policy_stats.active_policies = len([p for p in self.policies.values() 
                                                       if p.status == PolicyStatus.ACTIVE])
                
                self.logger.info(f"Added policy: {policy.name} ({policy.rule_id})")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add policy {policy.name}: {e}")
            return False
    
    def remove_policy(self, rule_id: str) -> bool:
        """Remove a policy rule from the engine."""
        try:
            with self._lock:
                if rule_id not in self.policies:
                    self.logger.warning(f"Policy {rule_id} not found")
                    return False
                
                policy = self.policies[rule_id]
                
                # Remove from index
                self._remove_from_index(policy)
                
                # Remove from storage
                del self.policies[rule_id]
                
                # Update statistics
                self.policy_stats.total_policies = len(self.policies)
                self.policy_stats.active_policies = len([p for p in self.policies.values() 
                                                       if p.status == PolicyStatus.ACTIVE])
                
                self.logger.info(f"Removed policy: {policy.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to remove policy {rule_id}: {e}")
            return False
    
    def evaluate_policies(self, context: PacketContext) -> List[PolicyEnforcementResult]:
        """
        Evaluate all applicable policies for a packet context.
        
        Args:
            context: PacketContext containing packet and classification data
            
        Returns:
            List of enforcement results for matched policies
        """
        start_time = time.time()
        results = []
        
        try:
            with self._lock:
                # Extract relevant fields for policy matching
                packet_data = self._extract_packet_data(context)
                
                # Find matching policies
                matching_policies = self._find_matching_policies(packet_data)
                
                # Sort by priority (highest first)
                matching_policies.sort(key=lambda p: p.priority.value)
                
                # Apply conflict resolution and enforce policies
                for policy in matching_policies:
                    if policy.status != PolicyStatus.ACTIVE:
                        continue
                    
                    # Check if policy has expired
                    if policy.expiry_time and time.time() > policy.expiry_time:
                        policy.status = PolicyStatus.EXPIRED
                        continue
                    
                    # Execute policy action
                    enforcement_result = self._enforce_policy(policy, context, packet_data)
                    results.append(enforcement_result)
                    
                    # Update policy statistics
                    policy.match_count += 1
                    if enforcement_result.success:
                        policy.enforce_count += 1
                    
                    # For blocking policies, stop processing further policies
                    if policy.action == PolicyAction.BLOCK and enforcement_result.success:
                        break
                
                # Update global statistics
                processing_time = (time.time() - start_time) * 1000
                self._update_statistics(results, processing_time)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {e}")
            return []
    
    def _extract_packet_data(self, context: PacketContext) -> Dict[str, Any]:
        """Extract relevant packet data for policy matching."""
        packet = context.packet
        dpi_data = context.dpi_metadata
        classification_data = context.classification_metadata
        
        # Extract packet properties using the Packet class methods
        return {
            # Basic packet information from Packet class
            'src_ip': packet.src_ip,
            'dst_ip': packet.dst_ip,
            'src_port': packet.src_port,
            'dst_port': packet.dst_port,
            'protocol': packet.protocol,
            'packet_size': packet.length,
            'is_multicast': packet.is_multicast,
            'timestamp': packet.timestamp,
            'interface': packet.interface,
            'flow_key': packet.get_flow_key(),
            
            # DPI results from context metadata
            'application_protocol': dpi_data.get('protocol_identification', {}).get('application_protocol'),
            'codec': dpi_data.get('protocol_identification', {}).get('codec'),
            'encrypted': dpi_data.get('encryption_analysis', {}).get('is_encrypted', False),
            'signatures': [match.get('name') for match in dpi_data.get('signature_matches', [])],
            'confidence': dpi_data.get('protocol_identification', {}).get('confidence', 0.0),
            
            # Classification results from context metadata
            'traffic_category': classification_data.get('category'),
            'priority_level': classification_data.get('priority'),
            'bandwidth_class': classification_data.get('bandwidth_class'),
            'classification_confidence': classification_data.get('confidence', 0.0),
            
            # Additional context information
            'packet_id': context.packet_id,
            'processing_errors': len(context.errors),
            'total_processing_time': context.get_total_processing_time()
        }
    
    def _find_matching_policies(self, packet_data: Dict[str, Any]) -> List[PolicyRule]:
        """Find all policies that match the packet data."""
        matching_policies = []
        
        # Use index for faster lookups
        candidate_rule_ids = set()
        
        # Get candidates based on indexed fields
        for field, value in packet_data.items():
            if field in self.policy_index and value is not None:
                candidate_rule_ids.update(self.policy_index[field])
        
        # If no indexed matches, check all policies
        if not candidate_rule_ids:
            candidate_rule_ids = set(self.policies.keys())
        
        # Evaluate each candidate policy
        for rule_id in candidate_rule_ids:
            policy = self.policies.get(rule_id)
            if policy and self._evaluate_policy_conditions(policy, packet_data):
                matching_policies.append(policy)
        
        return matching_policies
    
    def _evaluate_policy_conditions(self, policy: PolicyRule, packet_data: Dict[str, Any]) -> bool:
        """Evaluate if all conditions in a policy are met."""
        if not policy.conditions:
            return True  # Policy with no conditions matches all traffic
        
        # Create cache key for this evaluation
        cache_key = f"{policy.rule_id}:{hash(str(sorted(packet_data.items())))}"
        if cache_key in self._condition_cache:
            return self._condition_cache[cache_key]
        
        # Evaluate all conditions (AND logic)
        result = True
        for condition in policy.conditions:
            if not self._evaluate_condition(condition, packet_data):
                result = False
                break
        
        # Cache result
        if len(self._condition_cache) < self._cache_max_size:
            self._condition_cache[cache_key] = result
        
        return result
    
    def _evaluate_condition(self, condition: PolicyCondition, packet_data: Dict[str, Any]) -> bool:
        """Evaluate a single policy condition."""
        field_value = packet_data.get(condition.field)
        condition_value = condition.value
        
        if field_value is None:
            return False
        
        # Handle case sensitivity for string comparisons
        if isinstance(field_value, str) and isinstance(condition_value, str):
            if not condition.case_sensitive:
                field_value = field_value.lower()
                condition_value = condition_value.lower()
        
        # Evaluate based on operator
        if condition.operator == "equals":
            return field_value == condition_value
        elif condition.operator == "not_equals":
            return field_value != condition_value
        elif condition.operator == "contains":
            return str(condition_value) in str(field_value)
        elif condition.operator == "starts_with":
            return str(field_value).startswith(str(condition_value))
        elif condition.operator == "ends_with":
            return str(field_value).endswith(str(condition_value))
        elif condition.operator == "in_list":
            return field_value in condition_value if isinstance(condition_value, list) else False
        elif condition.operator == "greater_than":
            return float(field_value) > float(condition_value)
        elif condition.operator == "less_than":
            return float(field_value) < float(condition_value)
        elif condition.operator == "between":
            if isinstance(condition_value, list) and len(condition_value) == 2:
                return condition_value[0] <= float(field_value) <= condition_value[1]
        elif condition.operator == "regex_match":
            import re
            return bool(re.search(str(condition_value), str(field_value)))
        
        return False
    
    def _enforce_policy(self, policy: PolicyRule, context: PacketContext, 
                       packet_data: Dict[str, Any]) -> PolicyEnforcementResult:
        """Execute the enforcement action for a matched policy."""
        start_time = time.time()
        
        try:
            # Create enforcement result
            result = PolicyEnforcementResult(
                rule_id=policy.rule_id,
                action_taken=policy.action,
                action_parameters=policy.action_parameters.copy()
            )
            
            # Initialize policy metadata if not present
            if 'policy_metadata' not in context.__dict__ or context.policy_metadata is None:
                context.policy_metadata = {}
            
            # Execute action based on type
            if policy.action == PolicyAction.ALLOW:
                # Allow traffic through (no action needed)
                context.policy_metadata['action'] = 'allow'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                
            elif policy.action == PolicyAction.BLOCK:
                # Mark packet for blocking
                context.policy_metadata['action'] = 'block'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                context.policy_metadata['block_reason'] = policy.description
                
            elif policy.action == PolicyAction.THROTTLE:
                # Apply bandwidth throttling
                bandwidth_limit = policy.action_parameters.get('bandwidth_mbps', 1)
                context.policy_metadata['action'] = 'throttle'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                context.policy_metadata['bandwidth_limit'] = bandwidth_limit
                
            elif policy.action == PolicyAction.PRIORITIZE:
                # Set QoS priority
                priority_level = policy.action_parameters.get('priority', 0)
                context.policy_metadata['action'] = 'prioritize'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                context.policy_metadata['priority_level'] = priority_level
                
            elif policy.action == PolicyAction.REDIRECT:
                # Redirect traffic to different destination
                redirect_target = policy.action_parameters.get('target')
                context.policy_metadata['action'] = 'redirect'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                context.policy_metadata['redirect_target'] = redirect_target
                
            elif policy.action == PolicyAction.LOG_ONLY:
                # Log the event without blocking
                context.policy_metadata['action'] = 'log'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                self._log_policy_match(policy, packet_data)
                
            elif policy.action == PolicyAction.QUARANTINE:
                # Quarantine suspicious traffic
                context.policy_metadata['action'] = 'quarantine'
                context.policy_metadata['rule_id'] = policy.rule_id
                context.policy_metadata['policy_name'] = policy.name
                context.policy_metadata['quarantine_duration'] = policy.action_parameters.get('duration_minutes', 60)
            
            # Add enforcement timestamp
            context.policy_metadata['enforcement_time'] = time.time()
            
            # Record enforcement
            result.processing_time_ms = (time.time() - start_time) * 1000
            self.enforcement_history.append(result)
            
            self.logger.debug(f"Enforced policy {policy.name}: {policy.action.value}")
            return result
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            # Add error to context
            context.add_error('policy', f"Policy enforcement failed for {policy.name}: {e}")
            
            self.logger.error(f"Policy enforcement failed for {policy.name}: {e}")
            return result
    
    def _load_default_policies(self) -> None:
        """Load default policies from configuration."""
        default_policies = [
            # Block known malicious traffic
            PolicyRule(
                name="Block Malicious Traffic",
                description="Block traffic with known malicious signatures",
                conditions=[
                    PolicyCondition(field="signatures", operator="contains", value="malware"),
                    PolicyCondition(field="signatures", operator="contains", value="trojan")
                ],
                action=PolicyAction.BLOCK,
                priority=PolicyPriority.CRITICAL
            ),
            
            # Prioritize voice calls
            PolicyRule(
                name="Prioritize Voice Calls",
                description="High priority for voice call traffic",
                conditions=[
                    PolicyCondition(field="traffic_category", operator="equals", value="voice_call"),
                    PolicyCondition(field="protocol", operator="equals", value="UDP")
                ],
                action=PolicyAction.PRIORITIZE,
                action_parameters={"priority": 0},
                priority=PolicyPriority.HIGH
            ),
            
            # Throttle streaming during business hours
            PolicyRule(
                name="Throttle Video Streaming",
                description="Limit video streaming bandwidth during business hours",
                conditions=[
                    PolicyCondition(field="traffic_category", operator="equals", value="video_streaming"),
                    PolicyCondition(field="bandwidth_class", operator="equals", value="high")
                ],
                action=PolicyAction.THROTTLE,
                action_parameters={"bandwidth_mbps": 5},
                priority=PolicyPriority.MEDIUM
            )
        ]
        
        # Add default policies
        for policy in default_policies:
            self.add_policy(policy)
        
        self.logger.info(f"Loaded {len(default_policies)} default policies")
    
    def _validate_policy(self, policy: PolicyRule) -> bool:
        """Validate a policy rule."""
        if not policy.name:
            return False
        
        if not policy.conditions and policy.action != PolicyAction.ALLOW:
            return False
        
        # Validate conditions
        for condition in policy.conditions:
            if not condition.field or not condition.operator:
                return False
        
        return True
    
    def _update_policy_index(self, policy: PolicyRule) -> None:
        """Update policy index for fast lookups."""
        for condition in policy.conditions:
            self.policy_index[condition.field].append(policy.rule_id)
    
    def _remove_from_index(self, policy: PolicyRule) -> None:
        """Remove policy from index."""
        for condition in policy.conditions:
            if condition.field in self.policy_index:
                try:
                    self.policy_index[condition.field].remove(policy.rule_id)
                except ValueError:
                    pass
    
    def _update_statistics(self, results: List[PolicyEnforcementResult], processing_time: float) -> None:
        """Update policy statistics."""
        self.policy_stats.total_matches += len(results)
        self.policy_stats.total_enforcements += len([r for r in results if r.success])
        
        # Update average processing time
        if self.policy_stats.total_matches > 0:
            total_time = self.policy_stats.average_processing_time_ms * (self.policy_stats.total_matches - 1)
            self.policy_stats.average_processing_time_ms = (total_time + processing_time) / self.policy_stats.total_matches
        
        # Update success rate
        if self.policy_stats.total_enforcements > 0:
            self.policy_stats.enforcement_success_rate = self.policy_stats.total_enforcements / self.policy_stats.total_matches
    
    def _log_policy_match(self, policy: PolicyRule, packet_data: Dict[str, Any]) -> None:
        """Log policy match for monitoring."""
        log_data = {
            "policy_id": policy.rule_id,
            "policy_name": policy.name,
            "action": policy.action.value,
            "flow_key": packet_data.get('flow_key'),
            "traffic_category": packet_data.get('traffic_category'),
            "protocol": packet_data.get('protocol')
        }
        self.json_logger.log_json(log_data)
    
    def get_statistics(self) -> PolicyStatistics:
        """Get policy engine statistics."""
        return self.policy_stats
    
    def get_active_policies(self) -> List[PolicyRule]:
        """Get all active policies."""
        return [p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]
    
    def cleanup_expired_policies(self) -> int:
        """Clean up expired policies and return count of removed policies."""
        current_time = time.time()
        expired_policies = []
        
        with self._lock:
            for policy in self.policies.values():
                if policy.expiry_time and current_time > policy.expiry_time:
                    expired_policies.append(policy.rule_id)
            
            for rule_id in expired_policies:
                self.remove_policy(rule_id)
        
        return len(expired_policies)
