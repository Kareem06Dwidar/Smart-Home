import tkinter as tk
from tkinter import messagebox
import socket
import threading
import speech_recognition as sr
# TCP and UDP Configuration
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
UDP_SERVER_IP = 'localhost'
UDP_SERVER_PORT = 6000
# Function to log messages in the GUI
def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)
# TCP Control Function
def tcp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
            command = f"{device} is now {state}"
            sock.sendall(command.encode())
            response = sock.recv(1024).decode()
            log_message(f"Sent to TCP: {command}\nResponse: {response}")
    except Exception as e:
        log_message(f"Error in TCP: {str(e)}")
# UDP Control Function
def udp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            command = f"{device} is now {state}"
            sock.sendto(command.encode(), (UDP_SERVER_IP, UDP_SERVER_PORT))
            response, _ = sock.recvfrom(1024)
            log_message(f"Sent to UDP: {command}\nResponse: {response.decode()}")
    except Exception as e:
        log_message(f"Error in UDP: {str(e)}")
# Speech Recognition Command Handler
def handle_voice_command(command):
    log_message(f"Voice Command Recognized: {command}")
    command = command.lower()
    # Handle Living Room Light commands
    if "living room light" in command:
        if "on" in command:
            tcp_control("Living Room Light", "ON")
            log_message("Living Room Light turned ON")
        elif "off" in command:
            tcp_control("Living Room Light", "OFF")
            log_message("Living Room Light turned OFF")
    
    # Handle Thermostat commands
    elif "thermostat" in command:
        if "set" in command:
            try:
                # Attempt to find the temperature value
                temp = int([word for word in command.split() if word.isdigit()][0])
                udp_control("Thermostat", f"{temp}°C")
                log_message(f"Thermostat set to {temp}°C")
            except (IndexError, ValueError):
                log_message("Invalid temperature value in command.")
    # Handle Security Camera commands
    elif "security camera" in command:
        if "activate" in command or "on" in command:
            tcp_control("Security Camera", "ON")
            log_message("Security Camera activated")
        elif "deactivate" in command or "off" in command:
            tcp_control("Security Camera", "OFF")
            log_message("Security Camera deactivated")
    # Handle Main Door lock/unlock commands
    elif "main door" in command:
        if "lock" in command:
            udp_control("Main Door", "Locked")
            log_message("Main Door locked")
        elif "unlock" in command:
            udp_control("Main Door", "Unlocked")  # Ensure "Unlocked" is sent
            log_message("Main Door unlocked")
    
    else:
        log_message("Command not recognized")
# Function to listen for a single voice command
def listen_for_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_message("Listening for commands...")
        try:
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
# GUI Setup
root = tk.Tk()
root.title("Smart Home Voice Command Center")
root.geometry("600x650")
# Create a label for the title
tk.Label(root, text="Smart Home Command Center", font=("Arial", 18)).pack(pady=10)
# Create the log display area
log_text = tk.Text(root, height=15, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
log_text.pack(padx=20, pady=10)
# Create status label to show current action
status_label = tk.Label(root, text="Press 'Start Voice Command' to begin.", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)
# Create buttons to start and stop listening
start_button = tk.Button(root, text="Start Voice Command", command=start_listening, font=("Arial", 12))
start_button.pack(pady=10)
stop_button = tk.Button(root, text="Stop Voice Command", command=stop_listening, font=("Arial", 12))
stop_button.pack(pady=10)
# Run the GUI
root.mainloop()