# Basic UDP Client
import socket


def udp_client(host='127.0.0.1', port=65433, message="temperature update"):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp_socket.sendto(message.encode(), (host, port))  # Send message
    response, _ = udp_socket.recvfrom(1024)  # Receive acknowledgment
    print(f"Server response: {response.decode()}")
    udp_socket.close()


# Send a sample update
udp_client()
