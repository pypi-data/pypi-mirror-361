import argparse
import time
import os
from scapy.all import PcapReader, sendp, Ether, conf
import pyshark

# CONFIG: You can change these as needed
DEFAULT_IFACE = "wlp0s20f3"
DEFAULT_PCAP_PATH = "/home/khushi/Downloads/crestron_pack.pcap"

def replay_with_scapy(pcap_file: str, iface: str, delay: float = 0.01, count: int = None):
    """
    Replay PCAP file directly using Scapy - sends actual packets to network.
    This preserves the original packet structure completely.
    """
    print(f"Replaying packets from {pcap_file} on interface {iface}")
    
    if not os.path.exists(pcap_file):
        print(f"[!] Error: PCAP file '{pcap_file}' not found!")
        return
    
    try:
        packet_count = 0
        with PcapReader(pcap_file) as pcap_reader:
            for pkt in pcap_reader:
                if count and packet_count >= count:
                    break
                    
                # Send the packet exactly as it was captured
                sendp(pkt, iface=iface, verbose=False)
                packet_count += 1
                
                print(f"Sent packet {packet_count}: {pkt.summary()}")
                time.sleep(delay)
                
    except Exception as e:
        print(f"[!] Error during replay: {e}")
    
    print(f"Replay complete. Sent {packet_count} packets.")

def analyze_with_custom_packet_class(pcap_file: str, handler):
    """
    Analyze PCAP file using your custom Packet class - for analysis only.
    This processes packets through your DPI system.
    """
    from src.core.factory import PacketFactory
    
    print(f"Analyzing packets from PCAP file: {pcap_file}")
    
    if not os.path.exists(pcap_file):
        print(f"[!] Error: PCAP file '{pcap_file}' not found!")
        return
    
    try:
        cap = pyshark.FileCapture(pcap_file)
        packet_count = 0
        
        for pkt in cap:
            try:
                packet_count += 1
                
                # Get raw packet data
                raw_data = None
                timestamp = time.time()
                
                if hasattr(pkt, 'frame_raw'):
                    try:
                        raw_data = bytes.fromhex(pkt.frame_raw.value)
                    except (AttributeError, ValueError):
                        pass
                
                if hasattr(pkt, 'sniff_timestamp'):
                    try:
                        timestamp = float(pkt.sniff_timestamp)
                    except (AttributeError, ValueError):
                        pass
                
                if raw_data:
                    # Use the factory to create a packet and its context
                    _, context = PacketFactory.create_packet_with_context(
                        raw_data=raw_data, 
                        timestamp=timestamp,
                        interface="pcap_file"
                    )
                    handler(context) # Pass the whole context
                else:
                    print(f"[!] Could not extract raw data for packet {packet_count}")
                
                time.sleep(0.001)  # Small delay
                
            except Exception as e:
                print(f"[!] Failed to process packet {packet_count}: {e}")
                continue
                
    except Exception as e:
        print(f"[!] Error reading PCAP file: {e}")
    finally:
        try:
            cap.close()
        except:
            pass
    
    print(f"Analysis complete. Processed {packet_count} packets.")

def replay_with_pyshark_simple(pcap_file: str):
    """
    Simple packet display using PyShark - just shows packet info.
    """
    print(f"Displaying packets from {pcap_file}")
    
    if not os.path.exists(pcap_file):
        print(f"[!] Error: PCAP file '{pcap_file}' not found!")
        return
    
    try:
        cap = pyshark.FileCapture(pcap_file)
        packet_count = 0
        
        for pkt in cap:
            packet_count += 1
            print(f"Packet {packet_count}:")
            
            # Display basic packet info
            if hasattr(pkt, 'ip'):
                print(f"  IP: {pkt.ip.src} -> {pkt.ip.dst}")
            if hasattr(pkt, 'tcp'):
                print(f"  TCP: {pkt.tcp.srcport} -> {pkt.tcp.dstport}")
            elif hasattr(pkt, 'udp'):
                print(f"  UDP: {pkt.udp.srcport} -> {pkt.udp.dstport}")
            
            print(f"  Length: {pkt.length}")
            print(f"  Protocol: {pkt.highest_layer}")
            print()
            
            time.sleep(0.1)  # Pause between packets
            
    except Exception as e:
        print(f"[!] Error reading PCAP file: {e}")
    finally:
        try:
            cap.close()
        except:
            pass
    
    print(f"Display complete. Showed {packet_count} packets.")

def main():
    parser = argparse.ArgumentParser(description="PCAP file replay and analysis tool")
    parser.add_argument('--mode', 
                       choices=['direct_replay', 'analyze', 'display'], 
                       required=True,
                       help="Mode: direct_replay (send to network), analyze (use custom Packet class), display (show packet info)")
    
    parser.add_argument('--pcap_path', default=DEFAULT_PCAP_PATH, help="Path to PCAP file")
    parser.add_argument('--iface', default=DEFAULT_IFACE, help="Network interface (for direct_replay)")
    parser.add_argument('--delay', type=float, default=0.01, help="Delay between packets in seconds")
    parser.add_argument('--count', type=int, help="Maximum number of packets to process")
    
    args = parser.parse_args()
    
    if args.mode == 'direct_replay':
        # This actually sends packets to the network
        replay_with_scapy(args.pcap_path, args.iface, args.delay, args.count)
        
    elif args.mode == 'analyze':
        # This uses your custom Packet class for analysis
        def packet_handler(context):
            packet = context.packet
            print(f"Analyzed packet: {packet.src_ip}:{packet.src_port} -> {packet.dst_ip}:{packet.dst_port}")
            print(f"  Protocol: {packet.protocol}, Size: {packet.length}, Multicast: {packet.is_multicast}")
            if packet.payload:
                print(f"  Payload size: {len(packet.payload)} bytes")
        
        analyze_with_custom_packet_class(args.pcap_path, packet_handler)
        
    elif args.mode == 'display':
        # Simple packet display
        replay_with_pyshark_simple(args.pcap_path)

if __name__ == "__main__":
    main()