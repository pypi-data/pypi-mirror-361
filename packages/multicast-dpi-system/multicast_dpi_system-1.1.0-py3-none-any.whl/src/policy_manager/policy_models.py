"""
Policy Manager Data Models

Core data structures for policy definition, enforcement, and monitoring
in the multicast DPI system.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Set
from enum import Enum
import time
import uuid

class PolicyAction(Enum):
    """Available policy enforcement actions"""
    ALLOW = "allow"
    BLOCK = "block"
    THROTTLE = "throttle"
    PRIORITIZE = "prioritize"
    REDIRECT = "redirect"
    LOG_ONLY = "log_only"
    QUARANTINE = "quarantine"

class PolicyPriority(Enum):
    """Policy priority levels for conflict resolution"""
    CRITICAL = 0    # Emergency/security policies
    HIGH = 1        # Business critical policies
    MEDIUM = 2      # Standard operational policies
    LOW = 3         # Best effort policies

class PolicyStatus(Enum):
    """Policy operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"

@dataclass
class PolicyCondition:
    """Represents a single policy condition"""
    field: str                              # e.g., "protocol", "src_ip", "dst_port"
    operator: str                           # e.g., "equals", "contains", "in_range"
    value: Union[str, int, List[str]]       # The value to match against
    case_sensitive: bool = False

@dataclass
class PolicyRule:
    """Complete policy rule with conditions and actions"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    conditions: List[PolicyCondition] = field(default_factory=list)
    action: PolicyAction = PolicyAction.ALLOW
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    priority: PolicyPriority = PolicyPriority.MEDIUM
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_time: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    expiry_time: Optional[float] = None
    match_count: int = 0
    enforce_count: int = 0

@dataclass
class PolicyEnforcementResult:
    """Result of policy enforcement on a packet/flow"""
    rule_id: str
    action_taken: PolicyAction
    action_parameters: Dict[str, Any]
    enforcement_time: float = field(default_factory=time.time)
    success: bool = True
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0

@dataclass
class PolicyStatistics:
    """Statistics for policy monitoring and reporting"""
    total_policies: int = 0
    active_policies: int = 0
    total_matches: int = 0
    total_enforcements: int = 0
    enforcement_success_rate: float = 0.0
    average_processing_time_ms: float = 0.0
    top_matched_rules: List[str] = field(default_factory=list)
    recent_violations: List[str] = field(default_factory=list)
