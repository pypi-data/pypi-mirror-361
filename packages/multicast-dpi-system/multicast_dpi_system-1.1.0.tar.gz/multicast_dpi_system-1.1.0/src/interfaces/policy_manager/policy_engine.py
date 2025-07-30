"""
Policy Engine Interface

This module defines the abstract interface for policy engines.
Different implementations can provide various policy evaluation capabilities
while maintaining a consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.core.packet_context import PacketContext


class IPolicyEngine(ABC):
    """
    Abstract interface for policy engines.
    
    This interface ensures that all policy engine implementations
    provide consistent methods for policy evaluation and enforcement.
    """
    
    @abstractmethod
    def add_policy(self, policy: Any) -> bool:
        """
        Add a new policy rule to the engine.
        
        Args:
            policy: Policy rule to add
            
        Returns:
            bool: True if policy was added successfully
        """
        pass
    
    @abstractmethod
    def remove_policy(self, rule_id: str) -> bool:
        """
        Remove a policy rule from the engine.
        
        Args:
            rule_id: ID of the policy to remove
            
        Returns:
            bool: True if policy was removed successfully
        """
        pass
    
    @abstractmethod
    def evaluate_policies(self, context: PacketContext) -> List[Any]:
        """
        Evaluate all applicable policies for a packet context.
        
        Args:
            context: PacketContext containing packet and classification data
            
        Returns:
            List of enforcement results for matched policies
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Any:
        """
        Get policy engine statistics.
        
        Returns:
            Policy statistics object
        """
        pass
    
    @abstractmethod
    def get_active_policies(self) -> List[Any]:
        """
        Get all active policies.
        
        Returns:
            List of active policy rules
        """
        pass
    
    @abstractmethod
    def cleanup_expired_policies(self) -> int:
        """
        Clean up expired policies and return count of removed policies.
        
        Returns:
            int: Number of expired policies removed
        """
        pass 