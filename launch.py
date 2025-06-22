#!/usr/bin/env python3
import os
import subprocess
import threading
import time
import webbrowser
from app import app
from colorama import Fore, Style

class TermuxLauncher:
    def __init__(self):
        self.serveo_url = None
    
    def show_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"""{Fore.GREEN}
      ██╗  ██╗███████╗██╗  ██╗████████╗███████╗ ██████╗██╗  ██╗
██║  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
███████║█████╗   ╚███╔╝    ██║   █████╗  ██║     ███████║
██╔══██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║     ██╔══██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝

    {Style.RESET_ALL}
    [✓] Version: 2.2.0
    [✓] GitHub: SAMSMIS01
    [✓] Telegram: https://t.me/hextechcar
    ---------------------------------------------------
    """)

    def start_serveo(self):
        print(f"\n{Fore.BLUE}[*] Initialisation du tunnel Serveo...{Style.RESET_ALL}")
        try:
            process = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8080", "serveo.net"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for _ in range(30):
                line = process.stderr.readline()
                if "Forwarding" in line:
                    url = next((p for p in line.split() if p.startswith("http://")), None)
                    if url:
                        print(f"\n{Fore.GREEN}╔══════════════════════════════════╗")
                        print(f"║  Lien Serveo généré avec succès  ║")
                        print(f"║  {url.ljust(32)}  ║")
                        print(f"╚══════════════════════════════════╝{Style.RESET_ALL}")
                        webbrowser.open(url)
                        return url
                time.sleep(1)
            
            print(f"{Fore.RED}[!] Échec après 30 secondes{Style.RESET_ALL}")
            return None

        except Exception as e:
            print(f"{Fore.RED}[!] Erreur Serveo: {e}{Style.RESET_ALL}")
            return None

    def run(self):
        # Vérifier les dépendances
        try:
            subprocess.run(["ssh", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            print(f"{Fore.RED}[!] SSH non installé. Exécutez 'pkg install openssh'{Style.RESET_ALL}")
            return

        # Démarrer Flask
        flask_thread = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=8080, threaded=True),
            daemon=True
        )
        flask_thread.start()

        self.show_banner()
        self.serveo_url = self.start_serveo()

        if self.serveo_url:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Fermeture du tunnel...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Mode local seulement: http://localhost:8080{Style.RESET_ALL}")

if __name__ == '__main__':
    launcher = TermuxLauncher()
    launcher.run()
