"""
Factory module for creating Packet and PacketContext objects.

This module provides utility functions for creating packet objects
and their associated contexts in a consistent manner.
"""
from typing import Optional, Tuple
import time

from .packet import Packet
from .packet_context import PacketContext


class PacketFactory:
    """Factory class for creating Packet and PacketContext objects."""
    
    @staticmethod
    def create_packet_with_context(
        raw_data: bytes, 
        timestamp: Optional[float] = None,
        interface: Optional[str] = None
    ) -> "Tuple[Packet, PacketContext]":
        """
        Create a Packet and its corresponding PacketContext.
        
        Args:
            raw_data: Raw packet bytes from the network
            timestamp: Optional timestamp (current time if None)
            interface: Optional interface name where packet was captured
            
        Returns:
            Tuple[Packet, PacketContext]: A tuple containing the packet and its context
        """
        # Create packet
        packet = Packet(
            raw_data=raw_data,
            timestamp=timestamp or time.time(),
            interface=interface
        )
        
        # Create context
        context = PacketContext(packet=packet)
        
        return packet, context
    
    @staticmethod
    def create_context_from_packet(packet: Packet) -> "PacketContext":
        """
        Create a PacketContext from an existing Packet.
        
        Args:
            packet: Existing Packet object
            
        Returns:
            PacketContext: New context object for the packet
        """
        return PacketContext(packet=packet)
