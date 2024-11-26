import cv2
import os
from ftplib import FTP
from datetime import datetime

# FTP Configuration
FTP_SERVER = '127.0.0.1'  # IP of the FTP server
FTP_PORT = 2121           # Port for FTP server
FTP_USERNAME = 'user'
FTP_PASSWORD = 'pass'
FTP_UPLOAD_FOLDER = '/'   # Root folder on the server

# Output folder for captured images
CAPTURE_FOLDER = "captures"
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

def log_message(message):
    """Log messages to the console."""
    print(message)


def capture_motion():
    """Capture motion using the camera and save an image."""
    log_message("Starting camera for motion detection...")

    # Open the camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        log_message("Error: Could not access the camera.")
        return None

    log_message("Camera accessed successfully. Detecting motion...")

    # Read two frames to detect motion
    ret, frame1 = camera.read()
    ret, frame2 = camera.read()

    try:
        while True:
            # Compute the difference between consecutive frames
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # If motion is detected, capture the image
            if contours:
                log_message("Motion detected! Capturing image...")

                # Save the image with a timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                capture_path = os.path.join(CAPTURE_FOLDER, f"motion_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame1)
                log_message(f"Image saved: {capture_path}")

                return capture_path

            # Update frames
            frame1 = frame2
            ret, frame2 = camera.read()

            # Break the loop with 'q' (Optional Debug Window)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


def upload_file_to_ftp(file_path):
    """Upload a file to the FTP server."""
    try:
        log_message(f"Uploading {file_path} to FTP server...")

        # Connect to FTP server
        with FTP() as ftp:
            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
            ftp.cwd(FTP_UPLOAD_FOLDER)

            # Upload the file
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)

            log_message(f"File '{file_path}' uploaded successfully to FTP server.")
    except Exception as e:
        log_message(f"FTP upload error: {str(e)}")


if __name__ == "__main__":
    log_message("Home Security Camera System Initialized")
    captured_file = capture_motion()
    if captured_file:
        upload_file_to_ftp(captured_file)
