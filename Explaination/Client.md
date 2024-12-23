# **Smart Home Project: Client**

---

## **1️⃣ What does this code do?**

This code serves as the **client application** for the Smart Home system. It allows users to:
- Control devices like lights, doors, and thermostats.
- Detect motion using a webcam.
- Send email notifications for motion events.
- Execute commands via TCP or UDP protocols.
- Use voice commands for device control.
- Interact with a user-friendly GUI.

---

## **2️⃣ Full Code Breakdown**

### **Imports**

```python
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
import cv2
from datetime import datetime
import speech_recognition as sr
```

#### **What does this block do?**
- **Imports essential libraries**:
  - `tkinter`: For building the graphical user interface (GUI).
  - `socket` & `ssl`: For TCP and UDP communication.
  - `smtplib` & `email.mime`: For sending email notifications.
  - `os`: For file and directory management.
  - `cv2`: OpenCV library for motion detection.
  - `datetime`: For timestamping captured images.
  - `speech_recognition`: For processing voice commands.

---

### **Email Configuration**

```
IMAP_SERVER = "imap.mailserver.com"
SMTP_SERVER = "smtp.mailserver.com"
EMAIL_ACCOUNT = "smart1home@mailserver.com"
EMAIL_PASSWORD = "123456789"
```

#### **What does this block do?**
- Configures the email settings:
  - **IMAP_SERVER**: Address for checking incoming emails (not used in this script).
  - **SMTP_SERVER**: Address for sending outgoing emails.
  - **EMAIL_ACCOUNT**: The email account used for notifications.
  - **EMAIL_PASSWORD**: Password for the email account.

---

### **GUI Configuration**

```python
root = tk.Tk()
root.title("Smart Home Voice Command Center")
root.geometry("600x650")
log_text = tk.Text(root, height=15, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
```

#### **What does this block do?**
- Creates the main **GUI window**:
  - **`root`**: The main application window.
  - **`log_text`**: A text box for displaying logs or messages.

---

### **Email Sending Function**

```python
def send_email(to_address, subject, body, image_path=None):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ACCOUNT
        message["To"] = to_address
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if image_path:
            with open(image_path, "rb") as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                message.attach(img)

        with smtplib.SMTP(SMTP_SERVER, 25) as server:
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_address, message.as_string())

        messagebox.showinfo("Email Sent", f"Email successfully sent to {to_address}!")
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")
```

#### **What does this block do?**
- Sends an email notification:
  - **`to_address`**: Recipient's email address.
  - **`subject`**: Email subject.
  - **`body`**: Email body content.
  - **`image_path`**: Optional attachment (e.g., motion-detected image).

---

### **Motion Detection**

```python
def capture_motion():
    log_message("Starting camera for motion detection...")
    camera = cv2.VideoCapture(0)
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
                capture_path = os.path.join("captures", f"motion_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame1)
                send_email(EMAIL_ACCOUNT, "Motion Detected", "Motion detected. See attached image.", capture_path)
                return capture_path

            frame1 = frame2
            ret, frame2 = camera.read()
            if not ret:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
```

#### **What does this block do?**
- Detects motion using OpenCV:
  - Captures and compares consecutive frames.
  - Detects differences (motion) using contour analysis.
  - Saves a timestamped image upon motion detection.
  - Sends an email notification with the captured image.

---

### **TCP and UDP Control**

```python
def send_tcp_command(command):
    try:
        context = ssl.create_default_context()
        context.load_verify_locations('server.crt')

        with socket.create_connection((TCP_SERVER_IP, TCP_SERVER_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=TCP_SERVER_IP) as secure_sock:
                secure_sock.sendall(command.encode())
                response = secure_sock.recv(1024).decode()
                log_message(f"TCP Response: {response}")
    except Exception as e:
        log_message(f"TCP Error: {str(e)}")
```

```python
def send_udp_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.sendto(command.encode(), (UDP_SERVER_IP, UDP_SERVER_PORT))
            response, _ = udp_sock.recvfrom(1024)
            log_message(f"UDP Response: {response.decode()}")
    except Exception as e:
        log_message(f"UDP Error: {str(e)}")
```

#### **What does this block do?**
- Sends commands to the server via TCP or UDP:
  - **TCP**: Establishes a secure connection using SSL/TLS.
  - **UDP**: Sends commands without connection overhead.

---

### **Voice Commands**

```python
def handle_voice_command(command):
    command = command.lower()
    if "light" in command:
        send_tcp_command("Light ON" if "on" in command else "Light OFF")
    elif "door" in command:
        send_tcp_command("Door LOCK" if "lock" in command else "Door UNLOCK")
    elif "thermostat" in command and "set" in command:
        try:
            temp = int([word for word in command.split() if word.isdigit()][0])
            send_udp_command(f"Thermostat SET {temp}")
        except (IndexError, ValueError):
            log_message("Could not extract temperature.")
```

#### **What does this block do?**
- Processes voice commands for device control:
  - Supports commands like "Turn on the light" or "Set thermostat to 22."
  - Uses **TCP** for light and door commands, **UDP** for thermostat control.

---

### **Main GUI Setup**

```python
root = tk.Tk()
root.title("Smart Home Voice Command Center")
root.geometry("600x650")
tk.Label(root, text="Smart Home Control Center", font=("Arial", 18)).pack(pady=10)
log_text.pack(padx=20, pady=10)
tk.Button(root, text="Start Voice Command", command=start_voice_command).pack(pady=10)
tk.Button(root, text="Start Motion Detection", command=start_motion_detection).pack(pady=10)
root.mainloop()
```

#### **What does this block do?**
- Sets up the **main GUI window** with buttons to start:
  - **Voice command processing**.
  - **Motion detection**.

---

## **3️⃣ Key Concepts**

### **1. Motion Detection**
- Uses OpenCV to compare consecutive frames and detect differences (motion).

### **2. TCP and UDP**
- **TCP**: Reliable, secure communication for critical commands.
- **UDP**: Lightweight, fast communication for thermostat control.

### **3. Email Notifications**
- Sends alerts for motion detection using SMTP.

### **4. GUI**
- Built with Tkinter, providing an interactive interface for users.

---

## **4️⃣ Key Questions You Might Be Asked**

### **1. How does the client detect motion?**
- Compares consecutive frames from the webcam using OpenCV.
- Detects motion through contour analysis.

### **2. Why use TCP for some commands and UDP for others?**
- **TCP**: Ensures reliable delivery for critical commands (e.g., light and door).
- **UDP**: Faster and lightweight for less critical tasks like thermostat updates.

### **3. How are voice commands processed?**
- Captures voice input, converts it to text, and maps it to a device action.

---
