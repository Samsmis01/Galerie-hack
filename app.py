#!/usr/bin/env python3
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import zipfile
from io import BytesIO
import shutil
from datetime import datetime
import mimetypes
import threading
from functools import wraps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'collected_data'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['SECRET_KEY'] = 'A2g8#!kL9$pX@z5R%3q6*JmNvB4wD7yE'  # Changez ceci en prod

# Authentification
auth = HTTPBasicAuth()
users = {"admin": "Fl3x!2024_Transfert"}  # Mot de passe robuste

@auth.verify_password
def verify_password(username, password):
    return users.get(username) == password

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_files():
    if 'photos' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    files = request.files.getlist('photos')
    if len(files) > 100:
        return jsonify({'error': 'Maximum 100 photos autorisées'}), 400
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            uploaded_files.append(unique_filename)
    
    return jsonify({
        'message': f'{len(uploaded_files)} images téléversées',
        'files': uploaded_files,
        'download_url': '/download_all'
    })

@app.route('/download_all')
@auth.login_required
def download_all():
    def generate():
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                zf.write(file_path, filename)
        memory_file.seek(0)
        yield memory_file.getvalue()
        shutil.rmtree(app.config['UPLOAD_FOLDER'])  # Suppression après DL
        os.makedirs(app.config['UPLOAD_FOLDER'])  # Recréation du dossier
    
    return Response(
        generate(),
        mimetype='application/zip',
        headers={'Content-Disposition': 'attachment; filename=photos.zip'}
    )

@app.route('/download/<filename>')
@auth.login_required
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

def run_server():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_server)
    flask_thread.start(
