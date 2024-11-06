# Part(1)--------------------------------------------------------------------------------
import tkinter as tk
from tkinter import messagebox
import random
import socket

# TCP and UDP Configuration
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 5000
UDP_SERVER_IP = 'localhost'
UDP_SERVER_PORT = 6000

# Function to simulate TCP control
def tcp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
            command = f"{device} is now {state}"
            sock.sendall(command.encode())
            response = sock.recv(1024).decode()
            messagebox.showinfo("TCP Command", response)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to simulate UDP control
def udp_control(device, state):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            command = f"{device} is now {state}"
            sock.sendto(command.encode(), (UDP_SERVER_IP, UDP_SERVER_PORT))
            response, _ = sock.recvfrom(1024)
            messagebox.showinfo("UDP Command", response.decode())
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to simulate reading temperature
def read_temperature():
    return random.randint(18, 30)

# Function to simulate energy usage
def get_energy_usage():
    return {
        "Living Room Light": random.uniform(0.1, 1.0),
        "Thermostat": random.uniform(0.5, 2.0),
        "Security Camera": random.uniform(0.1, 0.5),
        "Main Door Lock": random.uniform(0.05, 0.2)
    }
# Part(2)--------------------------------------------------------------------------------
# Main dashboard window
class SmartHomeApp(tk.Tk):
    def init(self):
        super().init()
        self.title("Smart Home Dashboard")
        self.geometry("500x700")

        # Set default colors for the app
        self.bg_color = "#FFFFFF"
        self.fg_color = "#000000"

        # Adding main sections
        tk.Label(self, text="Dashboard", font=("Arial", 18, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(5, 15))
        self.create_section("Living Room Light", self.toggle_light, is_toggle=True)
        self.create_section("Thermostat", self.set_thermostat, is_slider=True)
        self.create_section("Security Camera", self.toggle_camera, is_toggle=True)
        self.create_section("Main Door Lock", self.toggle_door_lock, is_toggle=True)

        # Temperature Monitoring
        tk.Label(self, text="Current Room Temperature", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(20, 5))
        self.temp_label = tk.Label(self, text=f"{read_temperature()}°C", bg=self.bg_color, font=("Arial", 16, "bold"))
        self.temp_label.pack()

        # Create Smart Alerts and Recommendations before updating temperature
        self.create_smart_alerts()
        self.update_temperature()

        # Create Energy Monitoring
        self.create_energy_monitor()

    def create_section(self, name, command, is_toggle=False, is_slider=False):
        """Create a device control with bold, colored labels and status indicators."""
        frame = tk.Frame(self, bg=self.bg_color, highlightbackground="gray", highlightthickness=1, pady=5)
        frame.pack(pady=10, padx=20, fill="x")

        # Device Name
        tk.Label(frame, text=name, font=("Arial", 12, "bold"), bg=self.bg_color, fg="blue").pack(side="left", padx=(5, 0))

        if is_toggle:
            state_var = tk.BooleanVar()
            status_label = tk.Label(frame, text="OFF", font=("Arial", 10, "bold"), fg="red", bg=self.bg_color)
            status_label.pack(side="right", padx=(0, 5))
            tk.Checkbutton(frame, text="ON/OFF", variable=state_var,
command=lambda: self.toggle_device(state_var, status_label, command), bg=self.bg_color,
                           fg=self.fg_color, selectcolor=self.bg_color).pack(side="right")
        elif is_slider:
            temp_var = tk.IntVar(value=22)
            tk.Scale(frame, from_=15, to=30, orient="horizontal", variable=temp_var,
                     command=lambda v: command(temp_var.get()), bg=self.bg_color, fg=self.fg_color).pack(side="right")

# Part(3)--------------------------------------------------------------------------------
def toggle_device(self, state_var, status_label, command):
    """Toggle device status with colored indicators."""
    state = "ON" if state_var.get() else "OFF"
    command(state_var.get())
    status_label.config(text=state, fg="green" if state == "ON" else "red")


def toggle_light(self, state):
    tcp_control("Living Room Light", "ON" if state else "OFF")


def set_thermostat(self, value):
    udp_control("Thermostat", f"{value}°C")


def toggle_camera(self, state):
    tcp_control("Security Camera", "ON" if state else "OFF")


def toggle_door_lock(self, state):
    udp_control("Main Door", "Locked" if state else "Unlocked")


def update_temperature(self):
    """Update the temperature label color based on the temperature value."""
    new_temp = read_temperature()
    color = "blue" if new_temp < 20 else "orange" if 20 <= new_temp < 25 else "red"
    self.temp_label.config(text=f"{new_temp}°C", fg=color)
    self.after(5000, self.update_temperature)
    self.update_smart_alerts(new_temp)


def create_energy_monitor(self):
    """Create energy usage section with simulated data."""
    tk.Label(self, text="Energy Usage (kWh)", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.fg_color).pack(
        pady=(20, 5))
    self.energy_usage_frame = tk.Frame(self, bg=self.bg_color)
    self.energy_usage_frame.pack(pady=10, padx=20, fill="x")
    self.update_energy_usage()


def update_energy_usage(self):
    for widget in self.energy_usage_frame.winfo_children():
        widget.destroy()

    energy_data = get_energy_usage()
    for device, usage in energy_data.items():
        frame = tk.Frame(self.energy_usage_frame, bg=self.bg_color)
        frame.pack(fill="x")
        tk.Label(frame, text=f"{device}: ", font=("Arial", 10, "bold"), bg=self.bg_color, fg="green").pack(side="left")
        tk.Label(frame, text=f"{usage:.2f} kWh", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color).pack(
            side="left")

    self.after(10000, self.update_energy_usage)


def create_smart_alerts(self):
    """Create Smart Alerts and Recommendations section."""
    tk.Label(self, text="Smart Alerts & Recommendations", font=("Arial", 14, "bold"), bg=self.bg_color,
             fg=self.fg_color).pack(pady=(20, 5))
    self.alerts_frame = tk.Frame(self, bg=self.bg_color)
    self.alerts_frame.pack(pady=10, padx=20, fill="x")
    self.update_smart_alerts(read_temperature())
# Part(4)--------------------------------------------------------------------------------   

def update_smart_alerts(self, temp):
        """Generate alerts based on current conditions."""
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        alerts = []
        if temp > 26:
            alerts.append("Temperature is high - consider closing windows or lowering thermostat.")
        elif temp < 19:
            alerts.append("Temperature is low - consider raising thermostat or checking heating.")

        if not alerts:
            alerts.append("No alerts. All systems are normal.")

        for alert in alerts:
            tk.Label(self.alerts_frame, text=alert, font=("Arial", 10), bg=self.bg_color, fg="red").pack(anchor="w")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.configure_style()
        self.toggle_button.config(text="Switch to Light Mode" if self.is_dark_mode else "Switch to Dark Mode",bg=self.bg_color, fg=self.fg_color)

    def configure_style(self):
        """Configure colors and styles based on the theme."""
        if self.is_dark_mode:
            self.bg_color = "#2E2E2E"
            self.fg_color = "#FFFFFF"
        else:
            self.bg_color = "#FFFFFF"
            self.fg_color = "#000000"

        self.config(bg=self.bg_color)
        for widget in self.winfo_children():
            widget.config(bg=self.bg_color, fg=self.fg_color)


# Run the app
if __name__ == "__main__":
    app = SmartHomeApp()
    app.mainloop()
