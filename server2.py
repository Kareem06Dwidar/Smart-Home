import socket
import threading

TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
UDP_SERVER_IP = 'localhost'
UDP_SERVER_PORT = 6000

# TCP server function
def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        tcp_sock.listen(5)
        print("TCP server is listening on port", TCP_SERVER_PORT)
        
        while True:
            # Accept a new connection
            conn, addr = tcp_sock.accept()
            print("TCP connection from:", addr)
            # Handle each connection in a new thread
            threading.Thread(target=handle_tcp_client, args=(conn,)).start()

def handle_tcp_client(conn):
    """Handle individual TCP client connection"""
    with conn:
        try:
            data = conn.recv(1024).decode()
            if data:
                print("Received TCP command:", data)
                response = f"TCP command '{data}' received and executed."
                conn.sendall(response.encode())
        except Exception as e:
            print("TCP client error:", e)

# UDP server function
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((UDP_SERVER_IP, UDP_SERVER_PORT))
        print("UDP server is listening on port", UDP_SERVER_PORT)
        
        while True:
            try:
                data, addr = udp_sock.recvfrom(1024)
                command = data.decode()
                print("Received UDP command from", addr, ":", command)
                response = f"UDP command '{command}' received and executed."
                udp_sock.sendto(response.encode(), addr)
            except Exception as e:
                print("UDP server error:", e)

# Run both servers concurrently
if __name__ == "__main__":
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    tcp_thread.start()
    udp_thread.start()
    
    # Keep the main thread running to prevent server from closing
    print("Server is running. Press Ctrl+C to stop.")
    try:
        tcp_thread.join()
        udp_thread.join()
    except KeyboardInterrupt:
        print("Server stopped.")
