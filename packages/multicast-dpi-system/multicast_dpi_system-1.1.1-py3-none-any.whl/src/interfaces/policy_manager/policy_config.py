"""
Policy Configuration Interface

This module defines the abstract interface for policy configuration managers.
Different implementations can provide various configuration management capabilities
while maintaining a consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IPolicyConfig(ABC):
    """
    Abstract interface for policy configuration managers.
    
    This interface ensures that all policy configuration implementations
    provide consistent methods for policy template and configuration management.
    """
    
    @abstractmethod
    def load_configuration(self) -> Dict[str, Any]:
        """
        Load policy configuration.
        
        Returns:
            Dictionary containing policy configuration
        """
        pass
    
    @abstractmethod
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration.
        
        Args:
            config: Configuration to save
            
        Returns:
            bool: True if save was successful
        """
        pass
    
    @abstractmethod
    def create_policy_from_template(self, template_category: str, template_name: str, 
                                  custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Create a policy rule from a template.
        
        Args:
            template_category: Category of the template
            template_name: Name of the template
            custom_parameters: Optional custom parameters for the policy
            
        Returns:
            Optional[Any]: Policy rule if created successfully, None otherwise
        """
        pass
    
    @abstractmethod
    def export_policies_to_file(self, policies: List[Any], export_path: str) -> bool:
        """
        Export policies to a file for backup or sharing.
        
        Args:
            policies: List of policies to export
            export_path: Path where to export the policies
            
        Returns:
            bool: True if export was successful
        """
        pass 