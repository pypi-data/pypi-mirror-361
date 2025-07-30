"""
Configuration Generator Interface

Defines the interface for configuration generators that convert policy decisions
to device-specific configuration formats.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.core.packet_context import PacketContext


class IConfigGenerator(ABC):
    """Interface for configuration generators."""
    
    @abstractmethod
    def generate_from_policies(self, policy_results: List[Dict[str, Any]]) -> str:
        """
        Convert policy results to device-specific configuration format.
        
        Args:
            policy_results: List of policy enforcement results from Policy Manager
            
        Returns:
            Device-specific configuration string
        """
        pass
    
    @abstractmethod
    def generate_from_packet_contexts(self, contexts: List[PacketContext]) -> str:
        """
        Generate configuration from packet contexts that have been processed
        through the policy manager.
        
        Args:
            contexts: List of packet contexts with policy metadata
            
        Returns:
            Device-specific configuration string
        """
        pass
    
    @abstractmethod
    def get_supported_vendors(self) -> List[str]:
        """Get list of supported vendor/device types."""
        pass
    
    @abstractmethod
    def get_configuration_format(self) -> str:
        """Get the configuration format/type this generator produces."""
        pass
