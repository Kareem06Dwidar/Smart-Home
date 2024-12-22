import tkinter as tk
import threading
import socket
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from ftplib import FTP
import os
import cv2
from datetime import datetime
import speech_recognition as sr

# === Server and FTP Configuration ===
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
UDP_SERVER_IP = 'localhost'
UDP_SERVER_PORT = 6000
SSL_CERT = 'server.crt'
FTP_SERVER = '127.0.0.1'
FTP_PORT = 2121
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'
FTP_UPLOAD_FOLDER = '/'
CAPTURE_FOLDER = "captures"
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# === Email Configuration ===
SMTP_SERVER = "smtp.mailserver.com"
EMAIL_ACCOUNT = "smart1home@mailserver.com"
EMAIL_PASSWORD = "123456789"

# === GUI Setup ===
root = tk.Tk()
root.title("Smart Home Control Center")
root.geometry("600x750")
log_text = tk.Text(root, height=20, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)

# Log Function
def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

# TCP Client with SSL
def send_tcp_command(command):
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(SSL_CERT)
        with socket.create_connection((TCP_SERVER_IP, TCP_SERVER_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=TCP_SERVER_IP) as secure_sock:
                secure_sock.sendall(command.encode())
                response = secure_sock.recv(1024).decode()
                log_message(f"TCP Response: {response}")
    except Exception as e:
        log_message(f"TCP Error: {str(e)}")

# UDP Client
def send_udp_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.sendto(command.encode(), (UDP_SERVER_IP, UDP_SERVER_PORT))
            response, _ = udp_sock.recvfrom(1024)
            log_message(f"UDP Response: {response.decode()}")
    except Exception as e:
        log_message(f"UDP Error: {str(e)}")

# === FTP Upload ===
def upload_file_to_ftp(file_path):
    try:
        with FTP() as ftp:
            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
            ftp.cwd(FTP_UPLOAD_FOLDER)
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
            log_message(f"File '{file_path}' uploaded successfully to FTP server.")
    except Exception as e:
        log_message(f"FTP upload error: {str(e)}")

# === Motion Detection ===
def capture_motion():
    log_message("Starting motion detection...")
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        log_message("Error: Could not access the camera.")
        return None

    ret, frame1 = camera.read()
    if not ret or frame1 is None:
        log_message("Error: Could not read the first frame from the camera.")
        camera.release()
        return None

    ret, frame2 = camera.read()
    if not ret or frame2 is None:
        log_message("Error: Could not read the second frame from the camera.")
        camera.release()
        return None

    try:
        while True:
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                capture_path = os.path.join(CAPTURE_FOLDER, f"motion_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame1)
                log_message(f"Motion detected! Image saved: {capture_path}")
                send_email(EMAIL_ACCOUNT, "Motion Detected", "Motion was detected. See the attached image.", capture_path)
                upload_file_to_ftp(capture_path)
                return capture_path

            frame1 = frame2
            ret, frame2 = camera.read()
            if not ret or frame2 is None:
                log_message("Error: Could not read the next frame.")
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

# === Email Sending Function ===
def send_email(to_address, subject, body, image_path=None):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ACCOUNT
        message["To"] = to_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        if image_path:
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    message.attach(img)
            else:
                log_message("Error: Image not found.")
                return

        with smtplib.SMTP(SMTP_SERVER, 25) as server:
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_address, message.as_string())
        log_message(f"Email sent to {to_address}.")
    except Exception as e:
        log_message(f"Email error: {str(e)}")

# === Voice Command ===
def handle_voice_command(command):
    log_message(f"Voice Command: {command}")
    command = command.lower()
    if "capture motion" in command:
        capture_motion()
    elif "living room light" in command:
        if "on" in command:
            send_tcp_command("Living Room Light ON")
        elif "off" in command:
            send_tcp_command("Living Room Light OFF")
    elif "thermostat" in command:
        if "set" in command:
            try:
                temp = int([word for word in command.split() if word.isdigit()][0])
                send_udp_command(f"Thermostat SET {temp}")
            except (IndexError, ValueError):
                log_message("Error: Invalid temperature value.")
    else:
        log_message("Command not recognized.")

def listen_for_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_message("Listening for voice command...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            handle_voice_command(command)
        except sr.UnknownValueError:
            log_message("Could not understand the voice input.")
        except sr.RequestError as e:
            log_message(f"Speech recognition error: {str(e)}")

# === GUI ===
tk.Label(root, text="Smart Home Control Center", font=("Arial", 18)).pack(pady=10)
log_text.pack(padx=20, pady=10)
tk.Button(root, text="Capture Motion", command=lambda: threading.Thread(target=capture_motion, daemon=True).start(), font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="Start Voice Command", command=lambda: threading.Thread(target=listen_for_voice, daemon=True).start(), font=("Arial", 12)).pack(pady=10)

# Main Loop
root.mainloop()
