import socket
import pcap

def capture_packets():
    # Open a live capture on the default network interface
    pc = pcap.pcap()

    # Start sniffing and print packet information
    for pkt in pc:
        # Extract packet information
        packet = pkt[0]
        packet_hex = ''.join(format(byte, '02x') for byte in packet)
        packet_info = pcap.datalink().name + ' packet captured'
        packet_length = len(packet)

        # Print packet information
        print(f'Packet captured: {packet_info}')
        print(f'Packet length: {packet_length} bytes')
        print(f'Packet hex: {packet_hex}')
        print('')

if __name__ == '__main__':
    capture_packets()