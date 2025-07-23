def analyze_packet(packet):
    # Check for unusual packet size
    if len(packet) > 1024:
        print("Suspicious packet size detected!")

    # Check for unusual packet contents
    if b"malicious_string" in packet:
        print("Suspicious packet contents detected!")

    # Check for unusual packet source IP
    if packet.src_ip == "192.168.1.100":
        print("Suspicious packet source IP detected!")

    # Check for unusual packet destination IP
    if packet.dst_ip == "8.8.8.8":
        print("Suspicious packet destination IP detected!")

    # Check for unusual packet protocol
    if packet.proto == "icmp":
        print("Suspicious packet protocol detected!")

    # If no suspicious activity found, print a success message
    else:
        print("Packet analysis complete. No suspicious activity found.")