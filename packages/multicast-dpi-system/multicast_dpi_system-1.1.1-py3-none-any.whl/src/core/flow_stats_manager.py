"""
Central Flow Statistics Management

Provides per-flow statistics tracking for all modules (DPI, classifier, policy, etc).
"""
from typing import Dict, Optional
from collections import defaultdict
import time
import threading
from dataclasses import dataclass, field

@dataclass
class FlowStatistics:
    """Statistics for classified flows."""
    flow_key: str
    packet_count: int = 0
    byte_count: int = 0
    duration: float = 0.0
    average_packet_size: float = 0.0
    packets_per_second: float = 0.0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    category: Optional[str] = None

class FlowStatsManager:
    """
    Manages flow statistics for traffic classification and policy enforcement.
    Tracks packet counts, byte counts, duration, and other metrics for each unique flow.
    """
    def __init__(self):
        self.flow_stats: Dict[str, FlowStatistics] = defaultdict(lambda: FlowStatistics(flow_key=""))
        self._cleanup_thread = None
        self._cleanup_thread_stop = threading.Event()
        self._cleanup_interval = 60  # seconds
        self._lock = threading.Lock()

    def get_flow_key(self, context) -> str:
        # Use the same format as Packet.get_flow_key() for consistency
        return context.get_flow_key()

    def update_flow_stats(self, context) -> FlowStatistics:
        flow_key = self.get_flow_key(context)
        
        # Debug: Check if flow_key is valid
        if not flow_key or flow_key == "None:None->None:None:None":
            print(f"WARNING: Invalid flow key generated: '{flow_key}'")
            print(f"Packet context: src_ip={context.packet.src_ip}, dst_ip={context.packet.dst_ip}, src_port={context.packet.src_port}, dst_port={context.packet.dst_port}, protocol={context.packet.protocol}")
        
        with self._lock:
            stats = self.flow_stats[flow_key]
            if not stats.flow_key:
                stats.flow_key = flow_key
                stats.first_seen = time.time()
            stats.packet_count += 1
            stats.byte_count += context.packet.length
            stats.last_seen = time.time()
            stats.duration = stats.last_seen - stats.first_seen
            if stats.duration > 0:
                stats.packets_per_second = stats.packet_count / stats.duration
            stats.average_packet_size = stats.byte_count / stats.packet_count
            return stats

    def get_flow_statistics(self) -> Dict[str, FlowStatistics]:
        with self._lock:
            return dict(self.flow_stats)

    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        current_time = time.time()
        expired_flows = []
        with self._lock:
            for flow_key, stats in list(self.flow_stats.items()):
                if current_time - stats.last_seen > max_age_seconds:
                    expired_flows.append(flow_key)
            for flow_key in expired_flows:
                del self.flow_stats[flow_key]

    def _cleanup_loop(self, max_age_seconds: int):
        while not self._cleanup_thread_stop.is_set():
            self.cleanup_old_flows(max_age_seconds)
            self._cleanup_thread_stop.wait(self._cleanup_interval)

    def start_cleanup_thread(self, max_age_seconds: int = 300, interval: int = 60):
        self._cleanup_interval = interval
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
        self._cleanup_thread_stop.clear()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, args=(max_age_seconds,), daemon=True)
        self._cleanup_thread.start()

    def stop_cleanup_thread(self):
        if self._cleanup_thread:
            self._cleanup_thread_stop.set()
            self._cleanup_thread.join()
            self._cleanup_thread = None 