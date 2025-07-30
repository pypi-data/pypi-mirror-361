"""
Core module for the Multicast DPI system.

This module provides the fundamental data structures (Packet and PacketContext)
that are used throughout the DPI processing pipeline.
"""

from .packet import Packet
from .packet_context import PacketContext

__all__ = ['Packet', 'PacketContext']

# Version information
__version__ = '0.1.0'
