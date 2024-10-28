# Basic TCP Server Setup
import socket

def start_tcp_server(host='127.0.0.1', port=65432):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()  # Listen for incoming connections
    print(f"TCP server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()  # Accept client connection
        print(f"Connected with {client_address}")
        client_socket.sendall("Connection successful".encode())  # Send acknowledgment
        client_socket.close()

# Start the server
start_tcp_server()
