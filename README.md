
# Multi-Client Reverse Shell

A Python-based reverse shell project featuring a multi-client controller and agent.
The controller manages multiple connected agents, providing options like interactive shell access, system information retrieval, screenshot capture, webcam photo, file upload/download, and persistence. 

## ✅ Requirements
- Python **3.8+** installed on both the Controller and Agent (for development).
- Windows environment for the Agent (recommended for full feature support).
- `pyinstaller` or similar tool to compile the `agent.py` into an **EXE**.
- Open port on the server to accept connections (default: **4444**).

## ✅ Usage

### 1️⃣ Agent
- Edit the `agent.py` file and configure the **`SERVER_IP`** and **`SERVER_PORT`** with the Controller's IP and PORT.
- Compile the agent to an EXE:
  
  ```bash
  pyinstaller --noconsole --onefile agent.py


### 2️⃣ Controller
- Edit Controller.py if needed to set:
  
  ```bash
  LISTEN_IP = '0.0.0.0'
  LISTEN_PORT = 2242

- Run the Controller:
  
  ```bash
  python Controller.py

✅ Features
- Multi-client management.
- Interactive remote shell.
- Screenshot capture.
- Webcam photo capture.
- System information retrieval.
- File upload/download.
- Persistence (startup folder injection).


### This tool is provided for educational and authorized security testing purposes only. The use of this tool is entirely at the user's own risk. You are solely responsible for any actions performed using this tool.

⚠️ Unauthorized use of this tool on systems without explicit permission is strictly prohibited and may violate local, state, and federal laws.

By using this tool, you agree that you have explicit authorization to test the target systems and that you will not use it for any malicious or illegal activities. The author assumes no liability for any misuse or damage caused.
