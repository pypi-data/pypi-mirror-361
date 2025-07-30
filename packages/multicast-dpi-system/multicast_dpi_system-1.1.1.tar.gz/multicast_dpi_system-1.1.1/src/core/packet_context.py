"""
Unified Packet Context Dataclass

This module defines the `PacketContext`, the central data structure that is
passed between all processing stages of the DPI pipeline.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid

from .packet import Packet


@dataclass
class PacketContext:
    """
    A unified data model for a packet and its associated metadata as it flows
    through the various processing modules of the DPI system.

    This acts as a "carrier" or "envelope" for the raw packet, allowing each
    module (DPI, Classifier, Policy Manager) to read results from previous
    stages and append its own analysis without modifying the core packet or
    interfering with other modules' data.

    Attributes:
        packet (Packet): The original, raw network packet object.
        packet_id (str): Unique identifier for tracking this packet.
        dpi_metadata (Dict[str, Any]):
            A dictionary to be populated by the DPI Engine with details like
            identified protocol, confidence, and other extracted metadata.
        classification_metadata (Dict[str, Any]):
            A dictionary to be populated by the Traffic Classifier with details
            like traffic category, priority tags, and bandwidth estimates.
        policy_metadata (Dict[str, Any]):
            A dictionary to be populated by the Policy Manager with details
            about which policies matched and the enforcement actions taken.
        timestamps (Dict[str, float]):
            A dictionary to track the entry/exit timestamps for each processing
            stage, useful for performance monitoring.
        errors (Dict[str, str]):
            A dictionary to log any non-fatal errors that occur in a stage,
            allowing the context to continue processing.
    """
    packet: Packet
    packet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dpi_metadata: Dict[str, Any] = field(default_factory=dict)
    classification_metadata: Dict[str, Any] = field(default_factory=dict)
    policy_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamps: Dict[str, float] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps with creation time."""
        self.timestamps["created"] = time.time()

    def add_error(self, stage: str, message: str) -> None:
        """
        Records a non-fatal error that occurred during a processing stage.

        Args:
            stage (str): The name of the stage where the error occurred
                         (e.g., 'dpi', 'classifier', 'policy').
            message (str): The error message.
        """
        self.errors[stage] = message

    def mark_entry(self, stage: str) -> None:
        """
        Records the timestamp when a packet enters a processing stage.
        
        Args:
            stage (str): The name of the processing stage.
        """
        self.timestamps[f"{stage}_entry"] = time.time()

    def mark_exit(self, stage: str) -> None:
        """
        Records the timestamp when a packet exits a processing stage.
        
        Args:
            stage (str): The name of the processing stage.
        """
        self.timestamps[f"{stage}_exit"] = time.time()
        
    def get_processing_time(self, stage: str) -> Optional[float]:
        """
        Calculates the time spent in a processing stage in milliseconds.
        
        Args:
            stage (str): The name of the processing stage.
            
        Returns:
            Optional[float]: Processing time in milliseconds or None if unavailable.
        """
        entry = self.timestamps.get(f"{stage}_entry")
        exit_time = self.timestamps.get(f"{stage}_exit")
        
        if entry and exit_time:
            return (exit_time - entry) * 1000  # Convert to milliseconds
        return None

    def get_total_processing_time(self) -> Optional[float]:
        """
        Calculate total time from creation to the last recorded 'exit' event.
        
        Returns:
            Optional[float]: Total processing time in milliseconds, or None if no
                             exit events are recorded.
        """
        created_at = self.timestamps.get("created")
        if not created_at:
            return None # Should not happen if __post_init__ runs

        last_exit = max(
            (v for k, v in self.timestamps.items() if k.endswith("_exit")),
            default=None
        )

        if last_exit is None:
            return None # No processing stages have completed yet

        return (last_exit - created_at) * 1000

    def has_errors(self) -> bool:
        """Check if any processing errors occurred."""
        return len(self.errors) > 0

    def get_flow_key(self) -> str:
        """Get the flow key from the underlying packet."""
        return self.packet.get_flow_key()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary for logging or serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the context.
        """
        return {
            "packet_id": self.packet_id,
            "packet_info": {
                "src_ip": self.packet.src_ip,
                "dst_ip": self.packet.dst_ip,
                "src_port": self.packet.src_port,
                "dst_port": self.packet.dst_port,
                "protocol": self.packet.protocol,
                "is_multicast": self.packet.is_multicast,
                "length": self.packet.length,
                "timestamp": self.packet.timestamp
            },
            "metadata": {
                "dpi": self.dpi_metadata,
                "classification": self.classification_metadata,
                "policy": self.policy_metadata
            },
            "processing": {
                "timestamps": self.timestamps,
                "errors": self.errors,
                "total_time_ms": self.get_total_processing_time()
            }
        }

    def __repr__(self):
        has_dpi = "Yes" if self.dpi_metadata else "No"
        has_class = "Yes" if self.classification_metadata else "No"
        has_policy = "Yes" if self.policy_metadata else "No"
        return (
            f"PacketContext(id={self.packet_id[:8]}..., packet={self.packet!r}, "
            f"dpi={has_dpi}, classification={has_class}, policy={has_policy}, "
            f"errors={len(self.errors)})"
        )
