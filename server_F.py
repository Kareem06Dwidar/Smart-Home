import socket
import ssl
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# === Server Configuration ===
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
UDP_SERVER_IP = 'localhost'
UDP_SERVER_PORT = 6000
SSL_CERT = 'server.crt'
SSL_KEY = 'server.key'
FTP_SERVER_IP = '127.0.0.1'
FTP_PORT = 2121
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'

# === Helper Functions for TCP and UDP Commands ===
def send_tcp_command(command):
    print(f"Executing via TCP: {command}")

def send_udp_command(command):
    print(f"Executing via UDP: {command}")

# === TCP Handler ===
def handle_tcp_client(conn, addr):
    print(f"TCP connection from {addr}")
    with conn:
        try:
            data = conn.recv(1024).decode()
            if data:
                print(f"Received TCP: {data}")
                response = f"Command '{data}' received and executed."
                conn.sendall(response.encode())
        except Exception as e:
            print(f"TCP Error: {str(e)}")

# === TCP Server with SSL ===
def tcp_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        tcp_sock.listen(5)
        print(f"TCP server listening on {TCP_SERVER_IP}:{TCP_SERVER_PORT}")
        with context.wrap_socket(tcp_sock, server_side=True) as secure_sock:
            while True:
                conn, addr = secure_sock.accept()
                threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()

# === UDP Server ===
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((UDP_SERVER_IP, UDP_SERVER_PORT))
        print(f"UDP server listening on {UDP_SERVER_IP}:{UDP_SERVER_PORT}")
        while True:
            try:
                data, addr = udp_sock.recvfrom(1024)
                command = data.decode()
                print(f"Received UDP from {addr}: {command}")
                response = f"UDP command '{command}' executed."
                udp_sock.sendto(response.encode(), addr)
            except Exception as e:
                print(f"UDP Error: {str(e)}")

# === FTP Server Setup ===
def setup_ftp_server():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, UPLOAD_FOLDER, perm='elradfmw')
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((FTP_SERVER_IP, FTP_PORT), handler)
    print(f"FTP server running on {FTP_SERVER_IP}:{FTP_PORT}")
    server.serve_forever()

# === Main Function ===
if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=setup_ftp_server, daemon=True).start()
    print("All servers are running. Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server stopped.")
