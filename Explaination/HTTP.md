# **Smart Home Project: HTTP Server**

---

## **1️⃣ What does this code do?**

This code implements the **HTTP server** for the Smart Home system. It:
- Provides a **web-based control panel** for managing devices like lights, doors, and thermostats.
- Updates and displays **device statuses** in real time.
- Handles **GET** and **POST** requests to control devices and update statuses.

---

## **2️⃣ Full Code Breakdown**

### **Imports**

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
```

#### **What does this block do?**
- Imports modules to implement an HTTP server:
  - **`HTTPServer`**: Provides the core server functionality.
  - **`BaseHTTPRequestHandler`**: Handles HTTP requests (GET, POST, etc.).
  - **`json`**: For encoding and decoding JSON data.

---

### **Device Status**

```python
class SmartHomeHTTPRequestHandler(BaseHTTPRequestHandler):
    device_status = {
        'light': 'OFF',
        'door': 'UNLOCKED',
        'thermostat': 'Not Set'
    }
```

#### **What does this block do?**
- Defines the initial status of devices:
  - **`light`**: OFF by default.
  - **`door`**: UNLOCKED by default.
  - **`thermostat`**: No temperature set initially.

---

### **GET Request Handling**

```python
def do_GET(self):
    if self.path == "/":
        self.show_home_page()
    elif self.path.startswith("/device/light/on"):
        self.device_status['light'] = 'ON'
        message = "Light is now ON."
    elif self.path.startswith("/device/light/off"):
        self.device_status['light'] = 'OFF'
        message = "Light is now OFF."
    elif self.path.startswith("/device/door/lock"):
        self.device_status['door'] = 'LOCKED'
        message = "Door is now LOCKED."
    elif self.path.startswith("/device/door/unlock"):
        self.device_status['door'] = 'UNLOCKED'
        message = "Door is now UNLOCKED."
    elif self.path.startswith("/device/status"):
        message = json.dumps(self.device_status)  # Return status as JSON
    else:
        message = "Unknown command."
    
    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write(message.encode('utf-8'))
```

#### **What does this block do?**
- **Handles GET requests** for:
  - Serving the **home page** when accessing `/`.
  - Turning the **light ON or OFF**.
  - Locking or unlocking the **door**.
  - Returning the current **device statuses** in JSON format.
- **Sends a response**:
  - **`send_response(200)`**: HTTP status code for success.
  - **`send_header`**: Specifies the response content type.
  - **`wfile.write`**: Sends the response message back to the client.

---

### **POST Request Handling**

```python
def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    
    try:
        data = json.loads(post_data)
        device = data.get('device')
        action = data.get('action')
        value = data.get('value')
        
        if device == 'thermostat' and action == 'set' and value.isdigit():
            self.device_status['thermostat'] = f"{value}°C"
            message = f"Thermostat set to {value}°C."
        else:
            message = "Invalid request format."
    except Exception as e:
        message = f"Error processing POST request: {e}"

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps({'message': message}).encode('utf-8'))
```

#### **What does this block do?**
- **Handles POST requests** for:
  - Updating the **thermostat** temperature.
  - Validating the request format to ensure correct fields and values.
- **Processes the POST request**:
  - Reads the request body to get JSON data.
  - Extracts fields like `device`, `action`, and `value`.
- **Sends a JSON response** with a success or error message.

---

### **Serving the Home Page**

```python
def show_home_page(self):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Home Control</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                text-align: center;
                padding: 20px;
            }}
            h1 {{ color: #555; }}
            .device-status {{
                margin-bottom: 20px;
                padding: 15px;
                background-color: #e8f4f8;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .status {{ font-size: 18px; margin: 10px 0; }}
            button {{
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                font-size: 16px;
                margin: 10px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }}
            button:hover {{ background-color: #45a049; }}
            .button-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }}
        </style>
    </head>
    <body>
        <h1>Smart Home Control</h1>
        <div class="device-status">
            <h2>Device Status</h2>
            <p class="status"><strong>Light:</strong> {self.device_status['light']}</p>
            <p class="status"><strong>Door:</strong> {self.device_status['door']}</p>
            <p class="status"><strong>Thermostat:</strong> {self.device_status['thermostat']}</p>
        </div>
        <div class="button-container">
            <button onclick="sendCommand('/device/light/on')">💡 Light ON</button>
            <button onclick="sendCommand('/device/light/off')">💡 Light OFF</button>
            <button onclick="sendCommand('/device/door/lock')">🔒 Lock Door</button>
            <button onclick="sendCommand('/device/door/unlock')">🔓 Unlock Door</button>
        </div>
        <input type="number" id="temperature" placeholder="22" min="16" max="30">
        <button onclick="setThermostat()">Set Temperature</button>
        <script>
            function sendCommand(path) {{
                fetch(path)
                    .then(response => response.text())
                    .then(result => alert(result))
                    .then(() => window.location.reload());
            }}
            function setThermostat() {{
                const tempValue = document.getElementById('temperature').value;
                if (tempValue) {{
                    fetch('/device', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ device: 'thermostat', action: 'set', value: tempValue }}),
                    }})
                    .then(response => response.json())
                    .then(data => alert(data.message))
                    .then(() => window.location.reload());
                }} else {{
                    alert('Please enter a valid temperature');
                }}
            }}
        </script>
    </body>
    </html>
    """
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(html.encode('utf-8'))
```

#### **What does this block do?**
- Serves the **control panel** for the Smart Home system.
- Displays:
  - **Device statuses** (light, door, thermostat).
  - Buttons to control devices and set the thermostat.
- Includes **JavaScript functions**:
  - `sendCommand()`: Sends GET requests for device control.
  - `setThermostat()`: Sends POST requests to update the thermostat.

---

### **Starting the Server**

```python
def start_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SmartHomeHTTPRequestHandler)
    print("HTTP server running on port 8080")
    httpd.serve_forever()
```

#### **What does this block do?**
- Starts the HTTP server:
  - Binds to port 8080.
  - Uses `SmartHomeHTTPRequestHandler` to handle requests.

---

## **3️⃣ Key Concepts**

### **1. GET and POST Requests**
- **GET**: Used for retrieving device statuses and controlling devices.
- **POST**: Used for updating thermostat values.

### **2. Device Status**
- Stored as a dictionary (`device_status`) and updated dynamically based on requests.

### **3. Web Interface**
- Built with HTML, CSS, and JavaScript.
- Provides a user-friendly interface for controlling devices.

---

## **4️⃣ Key Questions You Might Be Asked**

### **1. How does the server handle device control?**
- Uses **GET** requests for light and door commands.
- Uses **POST** requests for thermostat updates.

### **2. How does the web interface update device statuses?**
- Dynamically fetches and displays statuses from the `device_status` dictionary.

### **3. How do you extend this script to add a new device?**
- Add the device to the `device_status` dictionary.
- Add handlers in `do_GET` and `do_POST` for the new device.

---
