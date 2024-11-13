# ================================
#3: Client Side and GUI Setup
# ================================
import tkinter as tk
from tkinter import messagebox
import socket
import threading

# Function to log messages in the GUI
def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

# Function to send TCP command from the client
def tcp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to TCP server and send command
            sock.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
            command = f"{device} is now {state}"
            sock.sendall(command.encode())
            response = sock.recv(1024).decode()
            log_message(f"Sent to TCP: {command}\nResponse: {response}")
    except Exception as e:
        log_message(f"Error in TCP: {str(e)}")

# Function to send UDP command from the client
def udp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Send command to UDP server
            command = f"{device} is now {state}"
            sock.sendto(command.encode(), (UDP_SERVER_IP, UDP_SERVER_PORT))
            response, _ = sock.recvfrom(1024)
            log_message(f"Sent to UDP: {command}\nResponse: {response.decode()}")
    except Exception as e:
        log_message(f"Error in UDP: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("Smart Home Voice Command Center")
root.geometry("600x650")

# GUI Elements
tk.Label(root, text="Smart Home Command Center", font=("Arial", 18)).pack(pady=10)
log_text = tk.Text(root, height=15, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
log_text.pack(padx=20, pady=10)
status_label = tk.Label(root, text="Press 'Start Voice Command' to begin.", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)
start_button = tk.Button(root, text="Start Voice Command", command=start_listening, font=("Arial", 12))
start_button.pack(pady=10)
stop_button = tk.Button(root, text="Stop Voice Command", command=stop_listening, font=("Arial", 12))
stop_button.pack(pady=10)

# ================================
#4: Voice Command Handling
# ================================
import speech_recognition as sr

# Function to handle voice commands
def handle_voice_command(command):
    log_message(f"Voice Command Recognized: {command}")
    command = command.lower()

    # Check for device-specific commands
    if "living room light" in command:
        if "on" in command:
            tcp_control("Living Room Light", "ON")
            log_message("Living Room Light turned ON")
        elif "off" in command:
            tcp_control("Living Room Light", "OFF")
            log_message("Living Room Light turned OFF")

    elif "thermostat" in command:
        if "set" in command:
            try:
                # Extract temperature value from command
                temp = int([word for word in command.split() if word.isdigit()][0])
                udp_control("Thermostat", f"{temp}°C")
                log_message(f"Thermostat set to {temp}°C")
            except (IndexError, ValueError):
                log_message("Invalid temperature value in command.")

    elif "security camera" in command:
        if "activate" in command or "on" in command:
            tcp_control("Security Camera", "ON")
            log_message("Security Camera activated")
        elif "deactivate" in command or "off" in command:
            tcp_control("Security Camera", "OFF")
            log_message("Security Camera deactivated")

    elif "main door" in command:
        if "lock" in command:
            udp_control("Main Door", "Locked")
            log_message("Main Door locked")
        elif "unlock" in command:
            udp_control("Main Door", "Unlocked")
            log_message("Main Door unlocked")
    
    else:
        log_message("Command not recognized")

# Function to listen for a single voice command
def listen_for_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_message("Listening for commands...")
        try:
            # Capture audio and recognize text
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            log_message(f"You said: {text}")
            handle_voice_command(text)
        except sr.UnknownValueError:
            log_message("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            log_message(f"Request error: {e}")

# Function to continuously listen for voice commands
def continuous_listen():
    global listening
    listening = True
    while listening:
        listen_for_commands()

# Function to stop listening for voice commands
def stop_listening():
    global listening
    listening = False
    log_message("Voice command listening stopped.")
    status_label.config(text="Voice Command Stopped. Click 'Start Voice Command' to listen again.")
    start_button.config(state=tk.NORMAL)

# Start the voice command listener
def start_listening():
    status_label.config(text="Listening for commands...")
    start_button.config(state=tk.DISABLED)
    log_message("Starting voice command listener...")
    threading.Thread(target=continuous_listen, daemon=True).start()

# Run the GUI
root.mainloop()