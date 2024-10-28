# Basic UDP Server Setup
import socket

def start_udp_server(host='127.0.0.1', port=65433):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print(f"UDP server listening on {host}:{port}")

    while True:
        data, client_address = udp_socket.recvfrom(1024)  # Receive data
        print(f"Received data from {client_address}: {data.decode()}")
        udp_socket.sendto("Data received".encode(), client_address)  # Send acknowledgment

# Start the UDP server
start_udp_server()
