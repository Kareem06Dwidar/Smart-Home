from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# FTP Server Configuration
FTP_SERVER_IP = '127.0.0.1'  # Use 'localhost' or '127.0.0.1'
FTP_PORT = 2121
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'

def setup_ftp_server():
    """Set up and run a plain FTP server."""
    # Create upload directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Set up user authorization
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, UPLOAD_FOLDER, perm='elradfmw')  # Full permissions

    # Configure FTP handler
    handler = FTPHandler
    handler.authorizer = authorizer

    # Start FTP server
    server = FTPServer((FTP_SERVER_IP, FTP_PORT), handler)
    print(f"FTP server running on {FTP_SERVER_IP}:{FTP_PORT}")
    print(f"Username: {FTP_USERNAME}, Password: {FTP_PASSWORD}")
    print(f"Upload files to: {UPLOAD_FOLDER}")
    server.serve_forever()


if __name__ == "__main__":
    setup_ftp_server()
