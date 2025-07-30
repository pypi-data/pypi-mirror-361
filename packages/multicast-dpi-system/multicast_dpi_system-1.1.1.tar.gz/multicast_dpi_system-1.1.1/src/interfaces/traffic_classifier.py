"""
Traffic Classifier Interface

This module defines the abstract interface for traffic classifiers.
Different implementations can provide various classification capabilities
while maintaining a consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.packet_context import PacketContext


class ITrafficClassifier(ABC):
    """
    Abstract interface for traffic classifiers.
    
    This interface ensures that all traffic classifier implementations
    provide consistent methods for traffic classification and management.
    """
    
    @abstractmethod
    def classify_traffic(self, context: PacketContext) -> Any:
        """
        Classify traffic based on packet context and DPI results.
        
        Args:
            context: PacketContext containing the packet and DPI metadata
            
        Returns:
            Classification result object
        """
        pass
    
    @abstractmethod
    def get_classification_statistics(self) -> Dict[str, Any]:
        """
        Get classification statistics.
        
        Returns:
            Dictionary containing classification statistics
        """
        pass
    
    @abstractmethod
    def get_flow_statistics(self) -> Dict[str, Any]:
        """
        Get flow statistics for monitoring.
        
        Returns:
            Dictionary containing flow statistics
        """
        pass
    
    @abstractmethod
    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """
        Clean up old flow statistics to prevent memory leaks.
        
        Args:
            max_age_seconds: Maximum age in seconds before flows are cleaned up
        """
        pass
