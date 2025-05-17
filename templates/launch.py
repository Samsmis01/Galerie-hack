#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import time
import webbrowser
from app import app  # Import de votre application Flask

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""{Colors.GREEN}
      ██╗  ██╗███████╗██╗  ██╗████████╗███████╗ ██████╗██╗  ██╗
██║  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
███████║█████╗   ╚███╔╝    ██║   █████╗  ██║     ███████║
██╔══██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║     ██╔══██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝

    {Colors.END}
    [✓] Version: 2.2.0
    [✓] GitHub: SAMSMIS01
    [✓] Telegram: https://t.me/hextechcar
    [✓] Instagram: SAMSMIS01
    [✓] Email: hextech243@gmail.com
    ---------------------------------------------------
    """)

def start_serveo():
    print(f"\n{Colors.BLUE}[*] Initialisation du tunnel Serveo...{Colors.END}")
    try:
        # Configuration SSH optimisée pour Termux
        ssh_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-R", "80:localhost:8080", "serveo.net"
        ]
        
        process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Attendre la génération du lien
        for _ in range(30):  # Timeout 30 secondes
            line = process.stderr.readline()
            if "Forwarding" in line:
                url = next((p for p in line.split() if p.startswith("http://")), None)
                if url:
                    print(f"\n{Colors.GREEN}╔══════════════════════════════════╗")
                    print(f"║  Lien Serveo généré avec succès  ║")
                    print(f"║  {url.ljust(32)}  ║")
                    print(f"╚══════════════════════════════════╝{Colors.END}")
                    print(f"\n{Colors.YELLOW}[*] Ce lien sera actif tant que le tunnel est maintenu")
                    print(f"[*] Gardez ce terminal ouvert{Colors.END}")
                    webbrowser.open(url)
                    return url
            time.sleep(1)
        
        print(f"{Colors.RED}[!] Échec après 30 secondes{Colors.END}")
        return None

    except Exception as e:
        print(f"{Colors.RED}[!] Erreur Serveo: {str(e)}{Colors.END}")
        return None

def main():
    # Démarrer Flask dans un thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=8080),
        daemon=True
    )
    flask_thread.start()

    # Afficher le banner
    show_banner()
    
    # Démarrer automatiquement Serveo
    serveo_url = start_serveo()

    if serveo_url:
        try:
            # Maintenir le script actif
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}[!] Fermeture du tunnel...{Colors.END}")
    else:
        print(f"{Colors.RED}[!] Arrêt du système{Colors.END}")

if __name__ == '__main__':
    # Vérifier les dépendances pour Termux
    try:
        subprocess.run(["ssh", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except:
        print(f"{Colors.RED}[!] SSH n'est pas installé. Exécutez 'pkg install openssh'{Colors.END}")
        sys.exit(1)
    
    main()