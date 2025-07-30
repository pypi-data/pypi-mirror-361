"""
Core Packet Dataclass

This module defines the fundamental `Packet` object, which represents a raw
network packet and provides methods to access its basic L2/L3/L4 properties.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import socket
import struct

try:
    import dpkt
    from ipaddress import ip_address
except ImportError:
    # This allows the package to be imported even if dpkt is not installed,
    # which can be useful for documentation generation or partial use.
    dpkt = None
    ip_address = None


@dataclass
class Packet:
    """
    Represents a raw network packet, providing easy access to its headers.

    This class is the foundational data structure for a captured packet. It
    takes raw bytes and lazily parses network information upon request. It is
    designed to be lightweight and transportable.

    Attributes:
        raw_data (bytes): The complete raw packet data from the wire.
        timestamp (float): The UNIX timestamp when the packet was captured.
        length (int): The original length of the packet on the wire.
        interface (Optional[str]): The interface this packet was captured on.
    """
    raw_data: bytes
    timestamp: float = field(default_factory=time.time)
    length: int = 0
    interface: Optional[str] = None

    # Cached properties to avoid repeated parsing
    _eth: Optional[Any] = field(default=None, repr=False, init=False)
    _ip: Optional[Any] = field(default=None, repr=False, init=False)
    _transport: Optional[Any] = field(default=None, repr=False, init=False)

    def __post_init__(self):
        """Initializes the length if not provided."""
        if self.length == 0:
            self.length = len(self.raw_data)
        if dpkt is None:
            raise ImportError("The 'dpkt' library is required to parse packets. Please install it.")

    @property
    def eth(self) -> Any:
        """Parses and returns the Ethernet frame (dpkt.ethernet.Ethernet)."""
        if self._eth is None:
            try:
                self._eth = dpkt.ethernet.Ethernet(self.raw_data)
            except (dpkt.dpkt.UnpackError, IndexError):
                self._eth = None
        return self._eth

    @property
    def ip(self) -> Any:
        """Parses and returns the IP layer (dpkt.ip.IP or dpkt.ip6.IP6)."""
        if self._ip is None and self.eth and isinstance(self.eth.data, (dpkt.ip.IP, dpkt.ip6.IP6)):
            self._ip = self.eth.data
        return self._ip

    @property
    def transport(self) -> Any:
        """Parses and returns the transport layer (dpkt.tcp.TCP or dpkt.udp.UDP)."""
        if self._transport is None and self.ip:
            self._transport = self.ip.data
        return self._transport

    @property
    def is_multicast(self) -> bool:
        """Checks if the packet's destination is a multicast address."""
        if not self.ip:
            return False
        try:
            return ip_address(self.dst_ip).is_multicast
        except (ValueError, AttributeError):
            return False

    @property
    def protocol(self) -> Optional[str]:
        """Returns the transport layer protocol name (e.g., 'TCP', 'UDP')."""
        if not self.ip:
            return None
        protocol_map = {
            dpkt.ip.IP_PROTO_TCP: "TCP",
            dpkt.ip.IP_PROTO_UDP: "UDP",
            dpkt.ip.IP_PROTO_IGMP: "IGMP",
            dpkt.ip.IP_PROTO_ICMP: "ICMP",
        }
        return protocol_map.get(self.ip.p, f"IP_PROTO_{self.ip.p}")

    @property
    def src_ip(self) -> Optional[str]:
        """Returns the source IP address (IPv4/IPv6-safe)."""
        if not self.ip:
            return None
        src = self.ip.src
        if isinstance(src, bytes):
            if len(src) == 4:
                return socket.inet_ntoa(src)
            elif len(src) == 16:
                try:
                    return socket.inet_ntop(socket.AF_INET6, src)
                except Exception:
                    return str(src)
        elif isinstance(src, str):
            return src
        return str(src)

    @property
    def dst_ip(self) -> Optional[str]:
        """Returns the destination IP address (IPv4/IPv6-safe)."""
        if not self.ip:
            return None
        dst = self.ip.dst
        if isinstance(dst, bytes):
            if len(dst) == 4:
                return socket.inet_ntoa(dst)
            elif len(dst) == 16:
                try:
                    return socket.inet_ntop(socket.AF_INET6, dst)
                except Exception:
                    return str(dst)
        elif isinstance(dst, str):
            return dst
        return str(dst)

    @property
    def src_port(self) -> Optional[int]:
        """Returns the source port of the transport layer."""
        if not self.transport or not hasattr(self.transport, 'sport'):
            return None
        return self.transport.sport

    @property
    def dst_port(self) -> Optional[int]:
        """Returns the destination port of the transport layer."""
        if not self.transport or not hasattr(self.transport, 'dport'):
            return None
        return self.transport.dport

    @property
    def payload(self) -> Optional[bytes]:
        """Returns the transport layer payload."""
        if not self.transport or not hasattr(self.transport, 'data'):
            return None
        return self.transport.data

    def get_flow_key(self) -> str:
        """Generate a unique flow key for packet grouping."""
        return f"{self.src_ip}:{self.src_port}->{self.dst_ip}:{self.dst_port}:{self.protocol}"

    def __repr__(self):
        return (
            f"Packet(timestamp={self.timestamp:.2f}, "
            f"src={self.src_ip}:{self.src_port}, "
            f"dst={self.dst_ip}:{self.dst_port}, "
            f"proto={self.protocol}, len={self.length})"
        )
