
# Smart Home Project

## Overview

This project implements a **Smart Home Control System** that integrates device control, motion detection, email notifications, and an interactive user interface. It leverages **TCP**, **UDP**, **FTP**, and **HTTP** protocols for seamless communication and control.

---

## Features

### ✅ Device Control
- Control devices like **lights**, **doors**, and **thermostats**.
- Issue commands via HTTP, TCP, or UDP protocols.
- Real-time status updates displayed on the web interface.

### ✅ Motion Detection
- Detect motion using a webcam via OpenCV.
- Capture images upon motion detection.
- Send email alerts with captured images attached.
- Upload captured images to the FTP server for storage.

### ✅ Voice Commands
- Use voice commands for device operations (e.g., "Turn the light on").
- Voice processing powered by **Google Speech Recognition**.

### ✅ Email Notifications
- Get email notifications for motion detection and events.
- Configured with **hMailServer** and tested using **Thunderbird**.

### ✅ Interactive GUI
- Desktop GUI for local control of devices, motion detection, and viewing logs.

### ✅ Web Interface
- Browser-based control panel for managing devices and real-time statuses.

---

## Installation

### Prerequisites
- **Python 3.10** or higher
- **OpenSSL** (for SSL certificate generation)
- **hMailServer** (local email server)
- **Thunderbird** (email client for testing)

### Clone the Repository
```
git clone https://github.com/your-repo/smart-home.git
cd smart-home
```

### Install Dependencies
```
pip install opencv-python pyftpdlib speechrecognition
```

### Generate SSL Certificate and Key with OpenSSL
Run the following command to create an SSL certificate and private key:
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
```
1. Fill in the required details (e.g., country, organization, etc.).
2. Save the generated `server.key` and `server.crt` files in the project directory.

### Configure hMailServer
1. Install **hMailServer** and set up a local email server.
2. Create an account:
   - **Email**: `smart1home@mailserver.com`
   - **Password**: `123456789`

---

## Run the Project

### Start the Core Server
```
python server_F.py
```

### Start the HTTP Server
```
python HTTP.py
```

### Start the Client Application
```
python client.py
```

---

## Usage

### 🌐 Web Interface
- Access the control panel at:
  ```
  http://localhost:8080
  ```
- Use buttons to control lights, doors, and thermostats.
- View real-time device statuses.

### 💻 Desktop GUI
- Use the GUI to:
  - Start motion detection.
  - Execute voice commands.
  - View logs of executed commands.

### 🎙️ Voice Commands
- Example commands:
  - "Turn the light on."
  - "Set thermostat to 22."

### 📷 Motion Detection
- Automatically detects motion and captures images.
- Sends email notifications with images attached.
- Uploads captured images to the FTP server for storage.

---

## File Structure

```
smart-home/
├── client.py           # Client application
├── HTTP.py             # HTTP server for the web interface
├── server_F.py         # Core server (TCP, UDP, FTP)
├── server.crt          # SSL certificate (generated with OpenSSL)
├── server.key          # SSL private key (generated with OpenSSL)
├── server.csr          # Certificate signing request (optional)
```

---

## Notes

### Email Testing
- Use **Thunderbird** to send/receive test emails from `smart1home@mailserver.com`.
- Ensure **hMailServer** is running and configured properly.

### Debugging
- Check the terminal logs for outputs from the client, HTTP server, and core server.
- Use browser developer tools to inspect HTTP requests and responses.

---

## Team Members:
- Kareem Dwidar
- Mohamed Ahmed
- Nour El-Deen Osama
- Ibrahim Hassan
- Yasmin Kotb

