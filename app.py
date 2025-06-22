#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'collected_data'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB pour 100 photos
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Créer le dossier s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
            # Affichage dans la console Termux
            print(f"Image {i} reçue: {unique_filename}")
    
    # Créer un zip de toutes les images (optionnel)
    # Vous pouvez utiliser ce zip pour le téléchargement
    return jsonify({
        'message': f'{len(uploaded_files)} images téléversées avec succès',
        'files': uploaded_files,
        'download_url': '/download_all'  # Endpoint pour télécharger toutes les images
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

if __name__ == '__main__':
    print("Serveur prêt à recevoir des images...")
    print(f"Accédez à l'interface via: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)



