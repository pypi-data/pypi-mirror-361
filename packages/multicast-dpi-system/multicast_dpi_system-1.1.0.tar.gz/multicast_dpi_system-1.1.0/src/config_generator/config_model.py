"""
Simplified data models for Cisco policy translation.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class CiscoAction(Enum):
    """Cisco-specific policy actions"""
    PERMIT = "permit"
    DENY = "deny"
    SET_DSCP = "set dscp"
    POLICE = "police"

@dataclass
class CiscoRule:
    """Cisco configuration rule"""
    action: CiscoAction
    protocol: str = "ip"
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    dscp_value: Optional[int] = None
    bandwidth_limit: Optional[str] = None

@dataclass
class CiscoConfig:
    """Generated Cisco configuration"""
    access_lists: list
    class_maps: list
    policy_maps: list
    interface_configs: list
