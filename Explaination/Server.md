# **Smart Home Project: Server**

---

## **1️⃣ What does this code do?**

This code acts as the **core server** for the Smart Home system. It provides functionalities for:
- Device control using **TCP** and **UDP** protocols.
- Secure communication via **SSL/TLS**.
- File uploads and management through an **FTP server**.

---

## **2️⃣ Full Code Breakdown**

### **Imports**

```python
import socket
import ssl
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
```

#### **What does this block do?**
- **Imports essential modules**:
  - `socket`: For creating TCP and UDP servers.
  - `ssl`: For secure communication with SSL/TLS.
  - `threading`: For running multiple servers (TCP, UDP, FTP) simultaneously.
  - `pyftpdlib`: A library for implementing an FTP server.
  - `os`: For file and directory management.

---

### **Server Configuration**

```python
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
```

#### **What does this block do?**
- Configures the server settings:
  - **TCP_SERVER_IP/UDP_SERVER_IP**: The IP addresses where the servers will listen.
  - **TCP_SERVER_PORT/UDP_SERVER_PORT**: Ports for TCP and UDP communication.
  - **SSL_CERT/SSL_KEY**: SSL certificate and private key for secure communication.
  - **FTP_SERVER_IP/FTP_PORT**: FTP server address and port.
  - **UPLOAD_FOLDER**: Directory where uploaded files will be stored.
  - **FTP_USERNAME/FTP_PASSWORD**: Credentials for accessing the FTP server.

---

### **Helper Functions**

```python
def send_tcp_command(command):
    print(f"Executing via TCP: {command}")

def send_udp_command(command):
    print(f"Executing via UDP: {command}")
```

#### **What does this block do?**
- Defines helper functions to simulate command execution:
  - `send_tcp_command(command)`: Logs TCP commands.
  - `send_udp_command(command)`: Logs UDP commands.

---

### **TCP Handler**

```python
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
```

#### **What does this block do?**
- Handles incoming TCP client connections:
  - Receives a command from the client.
  - Logs the received command and sends a confirmation back to the client.

---

### **TCP Server**

```python
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
```

#### **What does this block do?**
- Sets up a **secure TCP server**:
  - Uses SSL/TLS for encrypted communication.
  - Listens for incoming client connections on the specified IP and port.
  - Spawns a new thread for each client to handle connections concurrently.

---

### **UDP Server**

```python
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
```

#### **What does this block do?**
- Sets up a **UDP server**:
  - Receives and logs incoming UDP commands.
  - Sends acknowledgment back to the client.

---

### **FTP Server**

```python
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
```

#### **What does this block do?**
- Sets up an **FTP server**:
  - Creates an upload folder if it doesn't exist.
  - Configures FTP user credentials.
  - Starts the FTP server to manage file uploads and downloads.

---

### **Main Function**

```python
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
```

#### **What does this block do?**
- Starts the TCP, UDP, and FTP servers concurrently using threads:
  - Each server runs independently on its own thread.
  - Keeps the script running indefinitely until manually stopped.

---

## **3️⃣ Key Concepts**

### **1. TCP and UDP Servers**
- **TCP**: Reliable and connection-oriented, ideal for commands requiring acknowledgment.
- **UDP**: Lightweight and connectionless, suitable for fast communication.

### **2. SSL/TLS**
- Ensures secure communication by encrypting TCP connections.
- Requires an SSL certificate (`server.crt`) and private key (`server.key`).

### **3. FTP Server**
- Manages file uploads and downloads using the `pyftpdlib` library.
- Provides user authentication and permission management.

---

## **4️⃣ Key Questions You Might Be Asked**

### **1. How does the TCP server ensure security?**
- By using SSL/TLS for encrypted communication.

### **2. What happens if the upload folder doesn't exist?**
- The script creates the folder automatically during FTP server setup.

### **3. Why are threads used in this script?**
- Threads allow the TCP, UDP, and FTP servers to run concurrently without blocking each other.

---
