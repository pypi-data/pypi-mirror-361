"""
DPI Engine Interface

This module defines the abstract interface for DPI engines.
Different implementations can provide various analysis capabilities
while maintaining a consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.packet_context import PacketContext


class DPIEngineInterface(ABC):
    """
    Abstract interface for DPI engines.
    
    This interface ensures that all DPI engine implementations
    provide consistent methods for packet analysis and management.
    """
    
    @abstractmethod
    def analyze_packet(self, context: PacketContext) -> None:
        """
        Analyze a packet through the DPI pipeline.
        
        Args:
            context: PacketContext containing the packet and metadata
            
        This method should process the packet through all analysis modules
        and add the results to the context's dpi_metadata.
        """
        pass
    
    @abstractmethod
    def get_module_stats(self) -> Dict[str, Any]:
        """
        Get statistics from all analysis modules.
        
        Returns:
            Dictionary containing statistics from each module
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the DPI engine and all its modules.
        
        This method should cleanly shut down all analysis modules
        and release any resources.
        """
        pass
