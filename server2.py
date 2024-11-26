import socket
import threading
import ssl
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# === Part 1: FTP Server Setup ===
# This section handles the FTP server setup, user authorization, and starting the server.
FTP_SERVER_IP = '127.0.0.1'
FTP_PORT = 2121
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'

def setup_ftp_server():
    """Set up and run an FTP server."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, UPLOAD_FOLDER, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer((FTP_SERVER_IP, FTP_PORT), handler)
    print(f"FTP server running on {FTP_SERVER_IP}:{FTP_PORT}")
    print(f"Username: {FTP_USERNAME}, Password: {FTP_PASSWORD}")
    print(f"Upload files to: {UPLOAD_FOLDER}")
    server.serve_forever()


# === Part 2: TCP Server Setup ===
# This section handles the TCP server setup, SSL configuration, and handling incoming connections.
SERVER_CERT = 'server.crt'
SERVER_KEY = 'server.key'
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000

def handle_tcp_client(conn):
    """Handle individual TCP client connection."""
    with conn:
        print("Client connected.")
        try:
            data = conn.recv(1024).decode()
            if data:
                print("Received:", data)
                response = f"Command '{data}' received and executed."
                conn.sendall(response.encode())
        except Exception as e:
            print("Error handling TCP client:", e)

def start_tcp_server():
    """Start an SSL-secured TCP server."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as server_sock:
        server_sock.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        server_sock.listen(5)
        print(f"TCP Server listening on {TCP_SERVER_IP}:{TCP_SERVER_PORT}")

        with context.wrap_socket(server_sock, server_side=True) as secure_sock:
            while True:
                conn, addr = secure_sock.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=handle_tcp_client, args=(conn,)).start()


# === Part 3: Server Entry Point ===
# This is where the FTP server and TCP server are started.
if __name__ == "__main__":
    print("Starting servers...")
    threading.Thread(target=start_tcp_server, daemon=True).start()
    setup_ftp_server()
