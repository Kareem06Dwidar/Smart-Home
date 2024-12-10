import socket
import ssl
import threading
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# === Server Configuration ===
SERVER_CERT = 'server.crt'
SERVER_KEY = 'server.key'
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
FTP_SERVER_IP = '127.0.0.1'
FTP_PORT = 2121
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'

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
    print(f"Username: {FTP_USERNAME}, Password: {FTP_PASSWORD}")
    print(f"Upload files to: {UPLOAD_FOLDER}")
    server.serve_forever()

# === TCP Server with SSL and Command Processing ===
def handle_tcp_client(conn):
    with conn:
        print(f"Client connected: {conn}")
        try:
            data = conn.recv(1024).decode()
            if data:
                print(f"Received command: {data}")
                response = process_command(data)
                conn.sendall(response.encode())
            else:
                conn.sendall("No command received.".encode())
        except Exception as e:
            print(f"Error handling TCP client: {e}")
            conn.sendall("Error processing the command.".encode())

def process_command(command):
    command = command.strip().lower()
    print(f"Processing command: {command}")
    
    if "light on" in command:
        return "Light is now ON."
    elif "light off" in command:
        return "Light is now OFF."
    elif "door lock" in command:
        return "Door is now LOCKED."
    elif "door unlock" in command:
        return "Door is now UNLOCKED."
    elif "thermostat set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            return f"Thermostat set to {temp}°C."
        except (IndexError, ValueError):
            return "Error: Temperature value not found in command."
    else:
        return "Unknown command."

def start_tcp_server():
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
                threading.Thread(target=handle_tcp_client, args=(conn,)).start()

if __name__ == "__main__":
    threading.Thread(target=setup_ftp_server, daemon=True).start()
    start_tcp_server()
