"""
Traffic Classification Module Data Models

Defines the core data structures for traffic classification in the multicast DPI system.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import time

class TrafficCategory(Enum):
    """Primary traffic categories for multicast streams"""
    VIDEO_STREAMING = "video_streaming"
    AUDIO_STREAMING = "audio_streaming"
    VOICE_CALL = "voice_call"
    VIDEO_CONFERENCE = "video_conference"
    GAMING = "gaming"
    WEB_TRAFFIC = "web_traffic"
    FILE_TRANSFER = "file_transfer"
    IPTV = "iptv"
    MULTICAST_CONTROL = "multicast_control"
    MULTICAST_ROUTING = "multicast_routing"
    UNKNOWN = "unknown"

class PriorityLevel(Enum):
    """QoS priority levels for traffic management (higher number = higher priority)"""
    LOW = 0        # Background applications (file transfer)
    MEDIUM = 1     # Standard applications (web browsing)
    HIGH = 2       # Interactive applications (gaming, live streaming)
    CRITICAL = 3   # Real-time applications (voice, video calls)

class BandwidthClass(Enum):
    """Bandwidth requirement classifications"""
    ULTRA_HIGH = "ultra_high"    # 4K/8K video (>20 Mbps)
    HIGH = "high"                # HD video (5-20 Mbps)
    MEDIUM = "medium"            # SD video, audio (1-5 Mbps)
    LOW = "low"                  # Voice, text (<1 Mbps)

@dataclass
class ClassificationResult:
    """Container for traffic classification results"""
    primary_category: TrafficCategory
    sub_categories: List[str] = field(default_factory=list)
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    bandwidth_class: BandwidthClass = BandwidthClass.MEDIUM
    confidence_score: float = 0.0
    classification_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
