import tkinter as tk
import threading
import socket
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from tkinter import messagebox
import os
import imaplib
import email
from email.header import decode_header
import cv2
from datetime import datetime
import speech_recognition as sr

# === Email Configuration ===
IMAP_SERVER = "imap.mailserver.com"  # Local IMAP server for checking email
SMTP_SERVER = "smtp.mailserver.com"  # Local SMTP server for sending email
EMAIL_ACCOUNT = "smart1home@mailserver.com"  # Replace with your local email account
EMAIL_PASSWORD = "123456789"  # Replace with your local password

# === FTP Configuration ===
FTP_SERVER = '127.0.0.1'
FTP_PORT = 2121
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'
FTP_UPLOAD_FOLDER = '/'  # Root folder on the server
CAPTURE_FOLDER = "captures"
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# === Email Sending Function ===
def send_email(to_address, subject, body, image_path=None):
    """Sends an email with the command's result or the captured image."""
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ACCOUNT
        message["To"] = to_address
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if image_path:
            if os.path.exists(image_path):  # Check if image exists
                with open(image_path, "rb") as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    message.attach(img)
            else:
                messagebox.showerror("Image Error", f"Image file not found: {image_path}")
                return

        with smtplib.SMTP(SMTP_SERVER, 25) as server:  # Using local SMTP server (hMailServer)
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_address, message.as_string())

        messagebox.showinfo("Email Sent", f"Email successfully sent to {to_address}!")
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")

# === Motion Detection ===
def capture_motion():
    """Detect motion using the camera and save an image."""
    _log_message("Starting camera for motion detection...")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        log_message("Error: Could not access the camera.")
        return None

    _log_message("Camera accessed successfully. Detecting motion...")

    ret, frame1 = camera.read()
    ret, frame2 = camera.read()
    if not ret:
        _log_message("Error: Could not read frames.")
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
                _log_message("Motion detected! Capturing image...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                capture_path = os.path.join(CAPTURE_FOLDER, f"motion_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame1)
                _log_message(f"Image saved: {capture_path}")
                send_email("smart1home@mailserver.com", "Motion Detected", "Motion was detected, see the attached image.", capture_path)
                return capture_path

            frame1 = frame2
            ret, frame2 = camera.read()
            if not ret:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

def start_motion_detection():
    """Start the motion detection process in a separate thread."""
    threading.Thread(target=capture_motion, daemon=True).start()

# === Email Check (IMAP) ===
def check_email():
    """Check for new emails in the inbox and execute commands."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            print("No new messages.")
            return

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Decode email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    print(f"New Email Subject: {subject}")

                    # Extract email body (if multipart)
                    body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Only process non-attachment parts
                            if "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    # Stop once we find a valid body part
                                    break
                                except Exception as e:
                                    print(f"Error decoding email body part: {e}")
                                    body = None
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except Exception as e:
                            print(f"Error decoding email body: {e}")
                            body = None

                    # Check if body is extracted and process the command
                    if body:
                        print(f"Email Body: {body}")
                        process_command(body)
                    else:
                        print("No valid body content found in the email.")

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"Error checking emails: {e}")

def process_command(command):
    """Process email content as a command."""
    print(f"Processing command: {command}")  # Added print statement to debug
    command = command.lower()  # Make sure the command is case-insensitive
    if "light" in command:
        send_secure_command("Light ON" if "on" in command else "Light OFF")
        send_email(EMAIL_ACCOUNT, "Command Executed", "Light command executed.")
    elif "door" in command:
        send_secure_command("Door LOCK" if "lock" in command else "Door UNLOCK")
        send_email(EMAIL_ACCOUNT, "Command Executed", "Door command executed.")
    elif "thermostat" in command and "set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            send_secure_command(f"Thermostat SET {temp}°C")
            send_email(EMAIL_ACCOUNT, "Command Executed", f"Thermostat set to {temp}°C.")
        except (IndexError, ValueError):
            send_email(EMAIL_ACCOUNT, "Command Error", "Could not extract temperature from the command.")
    else:
        send_email(EMAIL_ACCOUNT, "Command Error", "Unknown command received.")

# === GUI Setup ===
def log_message_gui(message):
    """Logs messages in the GUI."""
    root.after(0, lambda: _log_message(message))

def _log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_message_gui("Listening for a voice command...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            handle_voice_command(command)
        except sr.UnknownValueError:
            log_message_gui("Could not understand the voice input.")
        except sr.RequestError as e:
            log_message_gui(f"Speech recognition error: {e}")

def handle_voice_command(command):
    log_message_gui(f"Recognized Command: {command}")
    command = command.lower()

    if "light" in command:
        send_secure_command("Light ON" if "on" in command else "Light OFF")
        send_email(EMAIL_ACCOUNT, "Command Executed", "Light command executed.")
    elif "door" in command:
        send_secure_command("Door LOCK" if "lock" in command else "Door UNLOCK")
        send_email(EMAIL_ACCOUNT, "Command Executed", "Door command executed.")
    elif "thermostat" in command and "set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            send_secure_command(f"Thermostat SET {temp}°C")
            send_email(EMAIL_ACCOUNT, "Command Executed", f"Thermostat set to {temp}°C.")
        except (IndexError, ValueError):
            log_message_gui("Could not extract temperature.")
            send_email(EMAIL_ACCOUNT, "Command Error", "Failed to set thermostat.")
    else:
        log_message_gui("Unknown command.")
        send_email(EMAIL_ACCOUNT, "Command Error", "Unknown command received.")

# === GUI Layout ===
root = tk.Tk()
root.title("Smart Home System")
root.geometry("600x750")

tk.Label(root, text="Smart Home Control Center", font=("Arial", 18)).pack(pady=10)

log_text = tk.Text(root, height=20, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
log_text.pack(padx=20, pady=10)

status_label = tk.Label(root, text="Select an action below.", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)

# Add buttons for actions
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start Voice Command", command=lambda: threading.Thread(target=listen_for_command).start(), font=("Arial", 12))
start_button.grid(row=0, column=0, padx=5, pady=5)

motion_button = tk.Button(button_frame, text="Start Motion Detection", command=start_motion_detection, font=("Arial", 12))
motion_button.grid(row=0, column=1, padx=5, pady=5)

# === Main Loop ===
root.mainloop()