import socket
import threading

# TCP server
def tcp_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('localhost', 5000))
    tcp_sock.listen(5)
    print("TCP Server started on port 5000")

    while True:
        client_socket, addr = tcp_sock.accept()
        print(f"TCP Connection from {addr}")
        data = client_socket.recv(1024).decode()
        if data:
            print(f"Received TCP command: {data}")
            response = f"TCP command '{data}' executed."
            client_socket.send(response.encode())
        client_socket.close()

# UDP server
def udp_server():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('localhost', 6000))
    print("UDP Server started on port 6000")

    while True:
        data, addr = udp_sock.recvfrom(1024)
        print(f"Received UDP command from {addr}: {data.decode()}")
        response = f"UDP command '{data.decode()}' executed."
        udp_sock.sendto(response.encode(), addr)

# Running both servers in separate threads
if __name__ == "__main__":
    tcp_thread = threading.Thread(target=tcp_server)
    udp_thread = threading.Thread(target=udp_server)

    tcp_thread.start()
    udp_thread.start()
