#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'collected_data'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limite à 50MB

# Créer le dossier s'il n'existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour servir les fichiers statiques (CSS, JS, etc.)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Route améliorée pour l'upload
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'media' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier reçu',
                'timestamp': datetime.now().isoformat()
            }), 400

        file = request.files['media']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Nom de fichier vide',
                'timestamp': datetime.now().isoformat()
            }), 400

        # Générer un nom de fichier unique
        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)  # Retour au début du fichier après lecture
        filename = f"{file_hash}_{file.filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Sauvegarder le fichier
        file.save(save_path)

        # Enregistrer des métadonnées supplémentaires
        file_size = os.path.getsize(save_path)
        upload_time = datetime.now().isoformat()

        return jsonify({
            'status': 'success',
            'message': 'Fichier sauvegardé avec succès',
            'filename': filename,
            'original_filename': file.filename,
            'file_hash': file_hash,
            'file_size': file_size,
            'timestamp': upload_time,
            'download_url': f'/download/{filename}'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Route pour télécharger les fichiers
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': 'Fichier non trouvé',
            'timestamp': datetime.now().isoformat()
        }), 404

# Route pour lister les fichiers uploadés
@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat(),
                    'download_url': f'/download/{filename}'
                })
        return jsonify({
            'status': 'success',
            'files': files,
            'count': len(files),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Route pour obtenir des statistiques
@app.route('/stats', methods=['GET'])
def stats():
    try:
        total_files = 0
        total_size = 0
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                total_files += 1
                total_size += os.path.getsize(file_path)

        return jsonify({
            'status': 'success',
            'total_files': total_files,
            'total_size': total_size,
            'total_size_human': f"{total_size / (1024 * 1024):.2f} MB",
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Configuration du serveur
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        debug=True
    )
