The Smart Home Network  is an interactive system that allows users to monitor and control various smart home devices from a centralized interface. This project uses TCP and UDP protocols to manage device communication, enabling real-time monitoring and control of devices such as lights, thermostat, and security systems. The dashboard provides an intuitive graphical user interface (GUI) developed using Python’s Tkinter, allowing users to toggle device states, receive smart alerts, and track energy usage.

The project is structured with a client-server architecture:
- Server: A Python-based server that listens for incoming TCP and UDP connections to process device commands.
- Client: A responsive GUI dashboard that sends commands and receives device updates from the server.

Features:
- Device Control: Turn devices on/off and adjust settings using TCP for secure command transmission and UDP for real-time updates.
- Smart Alerts: Receive alerts for significant events, such as temperature thresholds or unusual usage patterns.
- Energy and Usage Monitoring: Track energy consumption and usage statistics for each device.

Technologies Used:
- Python: For server, client, and device logic.
- Socket Programming: To handle TCP/UDP communication.
- Tkinter: To build an interactive GUI for the dashboard.

This project serves as an efficient and scalable solution for modern smart homes, emphasizing ease of control, customization, and enhanced user experience.
