# Basic TCP Client Setup
import socket

def tcp_client(host='127.0.0.1', port=65432):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    response = client_socket.recv(1024)  # Receive acknowledgment from server
    print(f"Server response: {response.decode()}")
    client_socket.close()

# Run client to connect to server
tcp_client()
