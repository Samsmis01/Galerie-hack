#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import time
import webbrowser
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

# Configuration de l'application Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'collected_data'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB pour 100 photos
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Créer le dossier s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

# Routes Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'photos' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    files = request.files.getlist('photos')
    
    if len(files) > 100:
        return jsonify({'error': 'Maximum 100 photos autorisées'}), 400
    
    uploaded_files = []
    
    for i, file in enumerate(files, 1):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            uploaded_files.append(unique_filename)
            print(f"Image {i} reçue: {unique_filename}")
    
    return jsonify({
        'message': f'{len(uploaded_files)} images téléversées avec succès',
        'files': uploaded_files,
        'download_url': '/download_all'
    })

@app.route('/download_all')
def download_all():
    def generate():
        import zipfile
        from io import BytesIO
        
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                zf.write(file_path, filename)
        
        memory_file.seek(0)
        yield from memory_file
        
    response = Response(generate(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename=photos.zip'
    return response

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

def main():
    # Démarrer Flask dans un thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=8080, threaded=True, debug=False),
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
