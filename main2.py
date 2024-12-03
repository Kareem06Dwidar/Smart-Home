import tkinter as tk
import threading
import socket
import ssl
import cv2
from datetime import datetime
from ftplib import FTP
import speech_recognition as sr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from tkinter import messagebox
import os

# === Email Configuration ===
IMAP_SERVER = "imap.gmail.com"  # IMAP server for checking email (unused here)
EMAIL_ADDRESS = "kareemsmtp@gmail.com"  # Sender email address
PASSWORD = "kcic giob cibg mcgs"  # Email password/app password

def send_email(to_address, subject, body, image_path=None):
    """
    Sends an email using Gmail's SMTP server.
    Optionally attaches an image.
    
    Parameters:
    - to_address: Recipient email address.
    - subject: Subject of the email.
    - body: Text body of the email.
    - image_path: Path to the image to attach (optional).
    """
    try:
        # Create the email container
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_address
        message["Subject"] = subject

        # Add text content to the email
        message.attach(MIMEText(body, "plain"))

        # Attach image if provided
        if image_path:
            if os.path.exists(image_path):  # Check if image exists
                with open(image_path, "rb") as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    message.attach(img)
            else:
                messagebox.showerror("Image Error", f"Image file not found: {image_path}")
                return

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, PASSWORD)  # Authenticate
            server.sendmail(EMAIL_ADDRESS, to_address, message.as_string())  # Send email

        # Notify user of success
        messagebox.showinfo("Email Sent", f"Email successfully sent to {to_address}!")
    except Exception as e:
        # Notify user of error
        messagebox.showerror("Email Error", f"Failed to send email: {e}")


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

                # Send email with the captured image
                send_email(
                    to_address="kareem.dwidar2003@gmail.com",
                    subject="Motion Detected",
                    body="Motion was detected, see the attached image.",
                    image_path=capture_path
                )
                return capture_path

            frame1 = frame2
            ret, frame2 = camera.read()
            if not ret:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    """Detect motion using the camera and capture an image."""
    send_email("kareem.dwidar2003@gmail.com",'Camera Detection!','Movement found..', r"C:\Users\Kareem Dwidar\Downloads\photo_5931742804264993388_y.jpg")
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
