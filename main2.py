import tkinter as tk
import threading
import socket
import ssl
import cv2
import os
from datetime import datetime
from ftplib import FTP
import speech_recognition as sr

# === Part 1: FTP Client for Upload ===
# Handles file uploads to the FTP server.
FTP_SERVER = '127.0.0.1'
FTP_PORT = 2121
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'
FTP_UPLOAD_FOLDER = '/'
CAPTURE_FOLDER = "captures"
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

def upload_file_to_ftp(file_path):
    """Upload a file to the FTP server."""
    try:
        with FTP() as ftp:
            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
            ftp.cwd(FTP_UPLOAD_FOLDER)
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
            log_message(f"File '{file_path}' uploaded successfully.")
    except Exception as e:
        log_message(f"FTP upload error: {str(e)}")


# === Part 2: Camera (Motion Detection) ===
# Handles motion detection and captures images.
def capture_motion():
    """Detect motion using the camera and capture an image."""
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        log_message("Error: Could not access the camera.")
        return None

    ret, frame1 = camera.read()
    ret, frame2 = camera.read()
    if not ret:
        log_message("Error: Could not read frames.")
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
                log_message("Motion detected! Capturing image...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                capture_path = os.path.join(CAPTURE_FOLDER, f"motion_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame1)
                log_message(f"Image saved: {capture_path}")
                return capture_path

            frame1 = frame2
            ret, frame2 = camera.read()
            if not ret:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

def start_motion_detection():
    threading.Thread(target=_start_motion_detection, daemon=True).start()

def _start_motion_detection():
    file_path = capture_motion()
    if file_path:
        upload_file_to_ftp(file_path)


# === Part 3: Secure Command Sending ===
# Handles secure communication with the TCP server.
SERVER_CERT = 'server.crt'
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000

def send_secure_command(command):
    """Send a secure command to the server."""
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(SERVER_CERT)

        with socket.create_connection((TCP_SERVER_IP, TCP_SERVER_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=TCP_SERVER_IP) as secure_sock:
                log_message(f"Sending command: {command}")
                secure_sock.sendall(command.encode())
                response = secure_sock.recv(1024).decode()
                log_message(f"Response: {response}")
    except Exception as e:
        log_message(f"Error: {str(e)}")


# === Part 4: GUI Setup ===
# Handles the GUI layout and interaction logic.
def log_message(message):
    root.after(0, lambda: _log_message(message))

def _log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_message("Listening for a voice command...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            handle_voice_command(command)
        except sr.UnknownValueError:
            log_message("Could not understand the voice input.")
        except sr.RequestError as e:
            log_message(f"Speech recognition error: {e}")

def handle_voice_command(command):
    log_message(f"Recognized Command: {command}")
    command = command.lower()

    if "light" in command:
        send_secure_command("Light ON" if "on" in command else "Light OFF")
    elif "door" in command:
        send_secure_command("Door LOCK" if "lock" in command else "Door UNLOCK")
    elif "thermostat" in command and "set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            send_secure_command(f"Thermostat SET {temp}°C")
        except (IndexError, ValueError):
            log_message("Could not extract temperature.")
    else:
        log_message("Unknown command.")

root = tk.Tk()
root.title("Smart Home System")
root.geometry("600x750")

tk.Label(root, text="Smart Home Control Center", font=("Arial", 18)).pack(pady=10)

log_text = tk.Text(root, height=20, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
log_text.pack(padx=20, pady=10)

status_label = tk.Label(root, text="Select an action below.", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)

tk.Label(root, text="Voice Commands", font=("Arial", 14)).pack(pady=5)
start_button = tk.Button(root, text="Start Voice Command", command=lambda: threading.Thread(target=listen_for_command).start(), font=("Arial", 12))
start_button.pack(pady=5)

tk.Label(root, text="Motion Detection", font=("Arial", 14)).pack(pady=5)
motion_button = tk.Button(root, text="Start Motion Detection", command=start_motion_detection, font=("Arial", 12))
motion_button.pack(pady=5)

# === Part 5: Main Loop ===
# Starts the GUI main loop.
root.mainloop()
