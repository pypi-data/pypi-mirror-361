import argparse
import time
from scapy.all import Ether, IP, UDP, sendp, conf
import pyshark

# Import your system's Packet class
from src.core.packet import Packet

# CONFIG: You can change these as needed
DEFAULT_IFACE = "wlp0s20f3"
DEFAULT_PCAP_PATH = "/home/khushi/Downloads/crestron_pack.pcap"

def mimic_multicast_traffic(iface: str, group_ip: str, dst_port: int, src_port: int, payload: bytes, count: int, interval: float):
    """Send synthetic multicast packets using Scapy."""
    packet = Ether() / IP(dst=group_ip) / UDP(sport=src_port, dport=dst_port) / payload
    print(f"Sending {count} multicast packets to {group_ip}:{dst_port} on interface {iface} ...")
    sendp(packet, iface=iface, count=count, inter=interval, verbose=True)
    print("Done.")

def replay_pcapng_traffic(pcap_file: str, handler):
    """Replay PCAPNG file using PyShark and call the handler for each packet."""
    print(f"Replaying packets from PCAPNG file: {pcap_file}")
    cap = pyshark.FileCapture(pcap_file)
    try:
        for pkt in cap:
            try:
                raw_data = bytes.fromhex(pkt.frame_raw.value)
                timestamp = float(pkt.sniff_timestamp)
                packet = Packet(raw_data=raw_data, timestamp=timestamp)
                handler(packet)
                time.sleep(0.01)
            except Exception as e:
                print(f"[!] Failed to process a packet: {e}")
    except Exception as e:
        print(f"[!] Error reading PCAPNG file: {e}")
    finally:
        cap.close()
        print("Replay complete.")

def main():
    parser = argparse.ArgumentParser(description="Test DPI system with either synthetic multicast or PCAPNG replay")
    parser.add_argument('--mode', choices=['multicast', 'pcap'], required=True, help="Choose traffic test mode: multicast | pcap")
    
    # Multicast-specific args
    parser.add_argument('--iface', default=DEFAULT_IFACE, help="Network interface to send packets")
    parser.add_argument('--group', default="239.0.0.1", help="Multicast IP")
    parser.add_argument('--dst_port', type=int, default=5004)
    parser.add_argument('--src_port', type=int, default=4000)
    parser.add_argument('--payload', default="Hello, Multicast DPI!", help="Payload string")
    parser.add_argument('--count', type=int, default=100)
    parser.add_argument('--interval', type=float, default=0.05)
    
    # PCAP-specific args
    parser.add_argument('--pcap_path', default=DEFAULT_PCAP_PATH, help="Path to .pcapng file")

    args = parser.parse_args()

    if args.mode == 'multicast':
        mimic_multicast_traffic(
            iface=args.iface,
            group_ip=args.group,
            dst_port=args.dst_port,
            src_port=args.src_port,
            payload=args.payload.encode(),
            count=args.count,
            interval=args.interval
        )

    elif args.mode == 'pcap':
        def packet_handler(packet: Packet):
            """Custom handler for processing packets from PCAPNG."""
            print(f"Captured packet: {packet.src_ip} -> {packet.dst_ip}, Size: {len(packet.raw_data)} bytes")

        replay_pcapng_traffic(pcap_file=DEFAULT_PCAP_PATH, handler=packet_handler)

if __name__ == "__main__":
    main()
