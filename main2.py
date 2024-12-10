import tkinter as tk
import threading
import socket
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import messagebox
import os
import imaplib
import email
from email.header import decode_header
import cv2
from datetime import datetime

# === Email Configuration ===
IMAP_SERVER = "imap.gmail.com"  # IMAP server for checking email
EMAIL_ACCOUNT = "kareemsmtp@gmail.com"  # Replace with your email address
EMAIL_PASSWORD = "kcic giob cibg mcgs"  # Replace with your app password

# === FTP Configuration ===
FTP_SERVER = '127.0.0.1'
FTP_PORT = 2121
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'
FTP_UPLOAD_FOLDER = '/'
CAPTURE_FOLDER = "captures"
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# === Email Sending Function ===
def send_email(to_address, subject, body, image_path=None):
    """Sends an email using Gmail's SMTP server."""
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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_address, message.as_string()) 

        messagebox.showinfo("Email Sent", f"Email successfully sent to {to_address}!")
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")

# === Secure TCP Communication ===
def send_secure_command(command):
    """Send a secure command to the server and display the response on the GUI."""
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("server.crt")

        with socket.create_connection(('localhost', 5000)) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as secure_sock:
                print(f"Sending command: {command}")
                secure_sock.sendall(command.encode())
                response = secure_sock.recv(1024).decode()
                print(f"Response: {response}")
                log_message(response)  # Display server response on the GUI
    except Exception as e:
        print(f"Error sending secure command: {e}")
        log_message(f"Error sending command: {e}")

# === Motion Detection ===
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
                        # Traverse the email parts
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
                        # If not multipart, directly get the payload
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
        print("Command: Light ON/OFF detected.")
        send_secure_command("Light ON" if "on" in command else "Light OFF")
    elif "door" in command:
        print("Command: Door LOCK/UNLOCK detected.")
        send_secure_command("Door LOCK" if "lock" in command else "Door UNLOCK")
    elif "thermostat" in command and "set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            print(f"Command: Setting thermostat to {temp}°C.")
            send_secure_command(f"Thermostat SET {temp}°C")
        except (IndexError, ValueError):
            print("Error: Could not extract temperature from the command.")
    else:
        print("Unknown command.")

# === GUI Setup ===
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

tk.Label(root, text="Check Emails", font=("Arial", 14)).pack(pady=5)
check_email_button = tk.Button(root, text="Check Emails", command=check_email, font=("Arial", 12))
check_email_button.pack(pady=5)

# === Main Loop ===
root.mainloop()
