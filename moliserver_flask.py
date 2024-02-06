import os
import json
import urllib.request
import firebase_admin
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore
from flask import send_file

app = Flask(__name__)
url_root = '34.125.74.48'
cred = credentials.Certificate('credential/cedar-league-413120-9b8aa1847567.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return "¡Bienvenido a la aplicación Flask!"

@app.route('/images/<code>', methods=['GET'])
def retrieve_image(code):
    image_filename = os.path.join('images', '{}.jpg'.format(code))
    if os.path.exists(image_filename):
        return send_file(image_filename, mimetype='image/jpeg')
    else:
        return jsonify({'status': 'error', 'message': 'Imagen no encontrada'}), 404

@app.route('/upload', methods=['POST'])
def handle_upload():
    try:
        data = request.get_json()

        if 'dni' in data and 'id_participation' in data and 'name' in data and 'photo_url' in data:
            dni = str(data['dni'])
            id_participation = str(data['id_participation'])
            name = str(data['name'])
            photo_url = str(data['photo_url'])

            save_path = os.path.join('images', '{}_{}.jpg'.format(dni, id_participation))
            urllib.request.urlretrieve(photo_url, save_path)

            public_url = request.url_root + save_path

            record = {
                "dni": dni,
                "name": name,
                "photo_url": public_url
            }

            db.collection("moli_records").document(dni + "_" + id_participation).set(record)

            response_data = {'status': 'success', 'message': 'Datos recibidos y procesados correctamente', 'public_url': public_url}
            return jsonify(response_data), 200
        else:
            raise ValueError('Se requieren tanto "photo_url" como "code" en los datos JSON.')
    except json.JSONDecodeError as e:
        return jsonify({'status': 'error', 'message': 'Error al decodificar el cuerpo JSON: {}'.format(str(e))}), 400

if __name__ == '__main__':
    app.run( port=80)
