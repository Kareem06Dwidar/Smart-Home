# UDP Client with Real-Time Update
import socket

def udp_client_send_update(host='127.0.0.1', port=65433, update="motion detected"):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Send real-time update
    udp_socket.sendto(update.encode(), (host, port))
    response, _ = udp_socket.recvfrom(1024)  # Receive acknowledgment
    print(f"Server response: {response.decode()}")
    udp_socket.close()

# Example update
udp_client_send_update(update="temperature: 25C")
