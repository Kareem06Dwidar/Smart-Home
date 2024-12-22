from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SmartHomeHTTPRequestHandler(BaseHTTPRequestHandler):
    device_status = {
        'light': 'OFF',
        'door': 'UNLOCKED',
        'thermostat': 'Not Set'
    }

    def do_GET(self):
        """Handle GET requests to control devices or get device status."""
        message = "Unknown command."  # Default message to avoid UnboundLocalError

        if self.path == "/":
            self.show_home_page()
            return
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

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def do_POST(self):
        """Handle POST requests to update the device status."""
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

    def show_home_page(self):
        """Serve the Smart Home control page with buttons for device control."""
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
                h1 {{
                    color: #555;
                }}
                .device-status {{
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #e8f4f8;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .status {{
                    font-size: 18px;
                    margin: 10px 0;
                }}
                button {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px 30px;
                    font-size: 16px;
                    margin: 10px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
                button.danger {{
                    background-color: #f44336;
                }}
                button.danger:hover {{
                    background-color: #e63929;
                }}
                button.control {{
                    background-color: #2196F3;
                }}
                button.control:hover {{
                    background-color: #1e88e5;
                }}
                .button-container {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                }}
                .button-container button {{
                    flex: 1 1 150px;
                    max-width: 200px;
                }}
                input[type="number"] {{
                    width: 80px;
                    padding: 10px;
                    margin-right: 10px;
                    border-radius: 5px;
                    border: 1px solid #ccc;
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

            <h2>Control Panel</h2>
            <div class="button-container">
                <button class="control" onclick="sendCommand('/device/light/on')">💡 Light ON</button>
                <button class="danger" onclick="sendCommand('/device/light/off')">💡 Light OFF</button>
                <button class="control" onclick="sendCommand('/device/door/lock')">🔒 Lock Door</button>
                <button class="danger" onclick="sendCommand('/device/door/unlock')">🔓 Unlock Door</button>
            </div>

            <h2>Thermostat Control</h2>
            <input type="number" id="temperature" placeholder="22" min="16" max="30">
            <button class="control" onclick="setThermostat()">Set Temperature</button>

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
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
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


def start_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SmartHomeHTTPRequestHandler)
    print("HTTP server running on port 8080")
    httpd.serve_forever()


if __name__ == "__main__":
    start_http_server()
