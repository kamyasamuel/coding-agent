firewall_rules = {
    "inbound": [
        {"protocol": "tcp", "port": 22, "action": "allow"},
        {"protocol": "tcp", "port": 80, "action": "allow"},
        {"protocol": "tcp", "port": 443, "action": "allow"}
    ],
    "outbound": [
        {"protocol": "tcp", "port": 53, "action": "allow"},
        {"protocol": "udp", "port": 53, "action": "allow"}
    ]
}