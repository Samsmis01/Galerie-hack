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

# ... [Toutes vos autres routes conservées exactement comme dans votre code original] ...

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,  # Changé pour correspondre au port Serveo
        threaded=True,
        debug=False
    )