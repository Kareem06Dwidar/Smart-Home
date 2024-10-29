# TCP Client with Commands
import socket

def tcp_client_send_command(host='127.0.0.1', port=65432, command="lock door"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    # Send specific command
    client_socket.send(command.encode())
    response = client_socket.recv(1024)  # Receive acknowledgment
    print(f"Server response: {response.decode()}")
    client_socket.close()

# Example command
tcp_client_send_command(command="turn off light")
