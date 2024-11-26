import tkinter as tk
import socket
import ssl
import threading
import speech_recognition as sr

# SSL Configuration
SERVER_CERT = 'server.crt'
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000

# Function to log messages in the GUI
def log_message(message):
    """Log messages to the GUI."""
    root.after(0, lambda: _log_message(message))

def _log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

# Function to send a secure TCP command
def send_secure_command(command):
    """Send a command to the server securely using SSL."""
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

# Function to process voice commands
def handle_voice_command(command):
    """Process the voice command and map to actions."""
    log_message(f"Recognized Command: {command}")
    command = command.lower()

    if "light" in command:
        if "on" in command:
            send_secure_command("Light ON")
        elif "off" in command:
            send_secure_command("Light OFF")
    elif "door" in command:
        if "lock" in command:
            send_secure_command("Door LOCK")
        elif "unlock" in command:
            send_secure_command("Door UNLOCK")
    elif "thermostat" in command:
        if "set" in command:
            try:
                temp = int([word for word in command.split() if word.isdigit()][0])
                send_secure_command(f"Thermostat SET {temp}°C")
            except (IndexError, ValueError):
                log_message("Could not extract temperature from command.")
        else:
            log_message("Command not understood for thermostat.")
    else:
        log_message("Unknown command.")

# Function to listen for a single voice command
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

# Function to start voice command listening in a loop
def start_listening():
    """Start listening for voice commands."""
    status_label.config(text="Listening for commands...")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    threading.Thread(target=continuous_listen, daemon=True).start()

def stop_listening():
    """Stop listening for voice commands."""
    global listening
    listening = False
    log_message("Stopped listening for commands.")
    status_label.config(text="Voice command stopped.")
    start_button.config(state=tk.NORMAL)

def continuous_listen():
    """Continuously listen for commands."""
    global listening
    listening = True
    while listening:
        listen_for_command()

# GUI Setup
root = tk.Tk()
root.title("Smart Home Voice Command Center")
root.geometry("600x650")

tk.Label(root, text="Smart Home Command Center", font=("Arial", 18)).pack(pady=10)

log_text = tk.Text(root, height=15, width=70, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
log_text.pack(padx=20, pady=10)

status_label = tk.Label(root, text="Press 'Start Voice Command' to begin.", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)

start_button = tk.Button(root, text="Start Voice Command", command=start_listening, font=("Arial", 12))
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Voice Command", command=stop_listening, font=("Arial", 12), state=tk.DISABLED)
stop_button.pack(pady=10)

root.mainloop()
