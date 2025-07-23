import socket
import os

def scan_network():
    list_of_ips = []
    for ip in range(1, 255):
        addr = f"192.168.1.{ip}"
        res = os.system(f"ping -c 1 {addr} > /dev/null 2>&1")
        if res == 0:
            list_of_ips.append(addr)
    return list_of_ips

if __name__ == '__main__':
    active_ips = scan_network()
    print("Active devices on the network:")
    for ip in active_ips:
        print(ip)