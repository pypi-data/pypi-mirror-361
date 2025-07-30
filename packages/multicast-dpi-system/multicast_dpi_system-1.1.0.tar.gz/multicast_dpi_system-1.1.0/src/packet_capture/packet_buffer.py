"""
Modern packet buffer implementation with priority queues, memory management, and enhanced features.
"""
import time
from typing import Dict, List, Optional, Union, Tuple, Deque, Any
from collections import deque, defaultdict
from dataclasses import dataclass
from heapq import heappush, heappop
import threading
from pathlib import Path

from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager


@dataclass
class BufferStats:
    added_packets: int = 0
    retrieved_packets: int = 0
    dropped_packets: int = 0
    peak_usage: int = 0
    last_cleanup: float = time.time()

class PacketBuffer:
    """
    High-performance packet buffer with:
    - Priority-based queuing
    - Memory management
    - Thread safety
    - Advanced statistics
    - Dynamic priority adjustment
    - Buffer overflow/backpressure handling
    """

    def __init__(self, logging_manager: LoggingManager, buffer_config: dict, buffer_size: int = None):
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.config = buffer_config or {}
        self.max_size = buffer_size or self.config.get('size_mb', 64) * 1024 * 1024
        self.cleanup_threshold = self.config.get('auto_delete_threshold', 80) / 100
        self.checkpoint_interval = self.config.get('checkpoint_interval_sec', 120)
        self.priority_queues: Dict[int, Deque[PacketContext]] = defaultdict(deque)
        self._init_priority_queues(self.config.get('priority_queues', {0: "default"}))
        self.total_packets = 0
        self.packet_sizes: Dict[int, int] = defaultdict(int)
        self.stats = BufferStats()
        self.lock = threading.RLock()
        self.cleanup_lock = threading.Lock()
        self.on_overflow = None
        self.logger.info(f"Initialized PacketBuffer with max_size={self.max_size} bytes, "
                   f"cleanup_threshold={self.cleanup_threshold}, "
                   f"priority_queues={len(self.config.get('priority_queues', {0: 'default'}))}")

    def _init_priority_queues(self, priority_config: Dict) -> None:
        """Initialize priority queues from configuration"""
        if not priority_config:
            self.priority_queues[0] = deque(maxlen=self.max_size)
            return
            
        for priority_str, criteria in priority_config.items():
            try:
                priority = int(priority_str)
                self.priority_queues[priority] = deque(maxlen=self.max_size)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid priority level: {priority_str}")

    def register_overflow_callback(self, callback):
        """
        Register a callback to be called when a packet is dropped due to buffer overflow.
        The callback will be called with the dropped packet and current stats.
        """
        self.on_overflow = callback

    def add_packet(self, context: PacketContext, priority: Optional[int] = None) -> bool:
        """
        Add a packet context to the buffer with optional priority.
        Returns True if context was successfully added.
        """
        with self.lock:
            priority = self._determine_priority(context) if priority is None else priority
            priority = self._validate_priority(priority)
            
            if self._needs_cleanup():
                self._cleanup_old_packets()
            
            try:
                self.priority_queues[priority].append(context)
                self.total_packets += 1
                self.packet_sizes[priority] += 1
                self.stats.added_packets += 1
                self.stats.peak_usage = max(self.stats.peak_usage, self.total_packets)
                return True
            except Exception as e:
                self.logger.error(f"Failed to add packet context: {e}", exc_info=True)
                self.stats.dropped_packets += 1
                self.logger.warning(f"Buffer overflow: packet dropped (total dropped: {self.stats.dropped_packets})")
                if self.on_overflow:
                    try:
                        self.on_overflow(context, self.stats)
                    except Exception as cb_e:
                        self.logger.error(f"Overflow callback error: {cb_e}", exc_info=True)
                return False

    def get_next_packet(self) -> Optional[PacketContext]:
        """Get next packet context from highest priority non-empty queue."""
        with self.lock:
            for priority in sorted(self.priority_queues.keys()):
                queue = self.priority_queues[priority]
                if queue:
                    context = queue.popleft()
                    self.total_packets -= 1
                    self.packet_sizes[priority] -= 1
                    self.stats.retrieved_packets += 1
                    return context
            return None

    def get_packets(self, count: int = 1, priority: Optional[int] = None) -> List[PacketContext]:
        """
        Get multiple packet contexts, optionally filtered by priority.
        """
        with self.lock:
            contexts = []
            if priority is not None:
                queue = self.priority_queues.get(priority, deque())
                contexts.extend(self._get_from_queue(queue, count))
            else:
                remaining = count
                for priority in sorted(self.priority_queues.keys()):
                    queue = self.priority_queues[priority]
                    contexts.extend(self._get_from_queue(queue, remaining))
                    remaining = count - len(contexts)
                    if remaining <= 0:
                        break
            return contexts

    def _get_from_queue(self, queue: Deque[PacketContext], count: int) -> List[PacketContext]:
        """Helper to get contexts from a single queue"""
        contexts = []
        for _ in range(min(count, len(queue))):
            try:
                context = queue.popleft()
                self.total_packets -= 1
                self.stats.retrieved_packets += 1
                contexts.append(context)
            except IndexError:
                break
        return contexts

    def _determine_priority(self, context: PacketContext) -> int:
        """Determine packet priority based on metadata and content"""
        # Check explicit priority in metadata
        if 'priority' in context.classification_metadata:
            return self._validate_priority(context.classification_metadata['priority'])
            
        # Check traffic class
        traffic_class = context.classification_metadata.get('traffic_class')
        if traffic_class:
            buffer_config = self.config.get('buffer', {})
            priority_queues = buffer_config.get('priority_queues', {})
            for priority, criteria in priority_queues.items():
                if str(criteria).lower() == traffic_class.lower():
                    return self._validate_priority(int(priority))
        
        # Protocol/port based detection
        packet = context.packet
        protocol = packet.protocol.upper() if packet.protocol else ""
        dst_port = packet.dst_port
        
        buffer_config = self.config.get('buffer', {})
        priority_queues = buffer_config.get('priority_queues', {})
        for priority, criteria in priority_queues.items():
            criteria_str = str(criteria).upper()
            
            # Protocol match
            if protocol in criteria_str:
                return self._validate_priority(int(priority))
                
            # Port range match
            if "PORT" in criteria_str:
                port_part = criteria_str.split("PORT")[-1].strip()
                if self._match_port_range(dst_port, port_part):
                    return self._validate_priority(int(priority))
        
        return self._validate_priority(0)  # Default to lowest

    def _match_port_range(self, port: int, spec: str) -> bool:
        """Check if port matches a range specification"""
        try:
            if '-' in spec:
                start, end = map(int, spec.split('-'))
                return start <= port <= end
            return port == int(spec)
        except (ValueError, AttributeError):
            return False

    def _validate_priority(self, priority: int) -> int:
        """Ensure priority exists, fallback to nearest available"""
        if priority in self.priority_queues:
            return priority
        available = sorted(self.priority_queues.keys())
        if not available:
            raise RuntimeError("No priority queues configured")
        return min(available, key=lambda x: abs(x - priority))

    def _needs_cleanup(self) -> bool:
        """Check if buffer needs cleanup"""
        return (self.total_packets / self.max_size) >= self.cleanup_threshold

    def _cleanup_old_packets(self) -> int:
        """
        Cleanup old packets based on age and priority.
        Returns number of packets removed.
        """
        with self.cleanup_lock:
            target = int(self.max_size * 0.2)  # Target 20% reduction
            removed = 0
            current_time = time.time()
            
            # Clean from lowest priority first
            for priority in sorted(self.priority_queues.keys(), reverse=True):
                queue = self.priority_queues[priority]
                new_queue = deque()
                
                for context in queue:
                    packet_age = current_time - context.packet.timestamp
                    if packet_age > self.checkpoint_interval and removed < target:
                        removed += 1
                        self.stats.dropped_packets += 1
                    else:
                        new_queue.append(context)
                
                self.priority_queues[priority] = new_queue
                
                if removed >= target:
                    break
            
            self.total_packets -= removed
            self.stats.last_cleanup = current_time
            self.logger.info(f"Cleaned {removed} old packets")
            return removed

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get comprehensive buffer statistics"""
        with self.lock:
            return {
                'total_packets': self.total_packets,
                'usage_percentage': (self.total_packets / self.max_size * 100) if self.max_size else 0,
                'added_packets': self.stats.added_packets,
                'retrieved_packets': self.stats.retrieved_packets,
                'dropped_packets': self.stats.dropped_packets,
                'peak_usage': self.stats.peak_usage,
                'last_cleanup_ago_sec': time.time() - self.stats.last_cleanup
            }

    def clear(self) -> None:
        """Clear all queues in the buffer."""
        with self.lock:
            for queue in self.priority_queues.values():
                queue.clear()
            self.total_packets = 0
            self.packet_sizes.clear()
            self.logger.info("Packet buffer cleared")

    def reload_config(self, buffer_config: dict) -> None:
        """Reload buffer configuration from the source"""
        self.logger.info("Reloading buffer configuration...")
        with self.lock:
            self.config = buffer_config or {}
            self.max_size = self.config.get('size_mb', 64) * 1024 * 1024
            self.cleanup_threshold = self.config.get('auto_delete_threshold', 80) / 100
            self.checkpoint_interval = self.config.get('checkpoint_interval_sec', 120)
            # Re-initialize priority queues carefully
            new_priority_queues = defaultdict(deque)
            new_config = self.config.get('priority_queues', {0: "default"})
            for priority, criteria in new_config.items():
                 new_priority_queues[int(priority)] = self.priority_queues.get(int(priority), deque())
            self.priority_queues = new_priority_queues
            self.logger.info("Buffer configuration reloaded")

    def __len__(self) -> int:
        """Return the total number of packets in the buffer."""
        return self.total_packets

    def __contains__(self, item: Union[PacketContext, Any]) -> bool:
        """Check if a context is in any of the queues."""
        if not isinstance(item, PacketContext):
            return False
        with self.lock:
            for queue in self.priority_queues.values():
                if item in queue:
                    return True
        return False

    def shutdown(self) -> None:
        """Shutdown and clear the buffer"""
        self.clear()
        self.logger.info("Packet buffer shutdown complete.")