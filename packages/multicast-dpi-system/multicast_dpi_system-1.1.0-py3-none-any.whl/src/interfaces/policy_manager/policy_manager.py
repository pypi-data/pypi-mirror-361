"""
Policy Manager Interface

This module defines the abstract interface for policy managers.
Different implementations can provide various policy enforcement capabilities
while maintaining a consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.core.packet_context import PacketContext


class IPolicyManager(ABC):
    """
    Abstract interface for policy managers.
    
    This interface ensures that all policy manager implementations
    provide consistent methods for policy enforcement and management.
    """
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the policy manager and background services.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the policy manager and cleanup resources.
        """
        pass
    
    @abstractmethod
    def process_packet(self, context: PacketContext) -> List[Any]:
        """
        Process a packet through the policy engine.
        
        Args:
            context: PacketContext containing packet and analysis data
            
        Returns:
            List of policy enforcement results
        """
        pass
    
    @abstractmethod
    def add_policy(self, policy: Any) -> bool:
        """
        Add a new policy to the manager.
        
        Args:
            policy: Policy rule to add
            
        Returns:
            bool: True if policy was added successfully
        """
        pass
    
    @abstractmethod
    def remove_policy(self, rule_id: str) -> bool:
        """
        Remove a policy from the manager.
        
        Args:
            rule_id: ID of the policy to remove
            
        Returns:
            bool: True if policy was removed successfully
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
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive policy manager statistics.
        
        Returns:
            Dictionary containing policy manager statistics
        """
        pass
    
    @abstractmethod
    def create_policy_from_template(self, template_category: str, template_name: str,
                                  custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create and add a policy from a template.
        
        Args:
            template_category: Category of the template
            template_name: Name of the template
            custom_parameters: Optional custom parameters for the policy
            
        Returns:
            Optional[str]: Policy rule ID if created successfully, None otherwise
        """
        pass
    
    @abstractmethod
    def export_configuration(self, export_path: str) -> bool:
        """
        Export current policy configuration.
        
        Args:
            export_path: Path where to export the configuration
            
        Returns:
            bool: True if export was successful
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the policy manager and print statistics.
        """
        pass
