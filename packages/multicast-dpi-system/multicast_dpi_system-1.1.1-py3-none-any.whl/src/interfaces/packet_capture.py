"""
Abstract Base Class for Packet Capture Interfaces.

This module defines the contract that all packet capture implementations
in the system must adhere to.
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from src.core.packet_context import PacketContext


class IPacketCapture(ABC):
    """
    An abstract interface for a packet capture system.

    This class defines the essential methods for starting, stopping, and
    interacting with a packet capture source. It ensures that any capture
    implementation (e.g., live capture, from-file capture) can be used
    interchangeably by the rest of the DPI system.
    """

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initializes the packet capture source, setting up resources like
        network listeners or file handles.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass

    @abstractmethod
    def start(self, callback: Callable[[PacketContext], None]) -> bool:
        """
        Starts the packet capture process.

        This method should begin feeding PacketContext objects to the provided
        callback function. This is expected to be a non-blocking call,
        likely running the capture loop in a background thread.

        Args:
            callback: A callable that accepts a single PacketContext object.
                      This will be the entry point for the DPI pipeline.

        Returns:
            bool: True if the capture process started successfully, False otherwise.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the packet capture process and cleans up any resources.
        This should be a graceful shutdown.
        """
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """
        Returns the running state of the capture system.

        Returns:
            bool: True if the system is currently capturing packets, False otherwise.
        """
        pass