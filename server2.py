import socket
import threading
import ssl

# SSL Configuration
SERVER_CERT = 'server.crt'
SERVER_KEY = 'server.key'
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000

def handle_client(conn):
    """Handle individual client connection."""
    with conn:
        print("Client connected.")
        try:
            data = conn.recv(1024).decode()
            if data:
                print("Received:", data)
                response = f"Command '{data}' received and executed."
                conn.sendall(response.encode())
        except Exception as e:
            print("Error handling client:", e)

def start_server():
    """Start an SSL-secured server."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as server_sock:
        server_sock.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        server_sock.listen(5)
        print(f"Server listening on {TCP_SERVER_IP}:{TCP_SERVER_PORT}")

        with context.wrap_socket(server_sock, server_side=True) as secure_sock:
            while True:
                conn, addr = secure_sock.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    print("Secure server starting...")
    try:
        start_server()
    except KeyboardInterrupt:
        print("Server shutting down.")
