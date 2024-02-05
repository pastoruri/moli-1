import os
import urllib.request
import socket
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('credential/cedar-league-413120-9b8aa1847567.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Obtener la ruta y el código de la URL

        path_parts = self.path.split('/')
        if len(path_parts) == 3 and path_parts[1] == 'images':
            self.handle_retrieve(path_parts)
            
        else:
            # Respuesta predeterminada para otras solicitudes GET
            self.send_error(404)

    def handle_retrieve(self, path_parts):
        code = path_parts[2].split('.')[0]
        image_filename = os.path.join('images', '{}.jpg'.format(code))
        # Verificar si la imagen existe
        if os.path.exists(image_filename):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            # Leer y enviar la imagen como respuesta a la solicitud GET
            with open(image_filename, 'rb') as image_file:
                self.wfile.write(image_file.read())
        else:
            self.send_error(404, 'Imagen no encontrada')

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_error(404)

    def handle_upload(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            # Intenta parsear el cuerpo JSON de la solicitud POST
            data = json.loads(body)

            # Verifica si se proporcionaron tanto la URL de la foto como el código
            if 'dni' in data and 'id_participation' in data and 'name' in data and 'photo_url' in data:
                photo_url = str(data['photo_url'])
                name = str(data['name'])
                dni = str(data['dni'])
                id_participation = str(data['id_participation'])

                # Muestra la URL de la foto y el código en la consola del servidor
                print('URL de la foto:', photo_url)
                print('DNI:', dni)
                print('Participacion:', id_participation)


                # Descarga la imagen y guárdala en la carpeta "images"
                save_path = os.path.join(os.path.dirname(__file__), 'images')
                os.makedirs(save_path, exist_ok=True)

                image_filename = os.path.join(save_path, '{}_{}.jpg'.format(dni,id_participation))
                urllib.request.urlretrieve(photo_url, image_filename)

                print('Imagen guardada en:', image_filename)

                # Genera la URL pública del servidor
                public_ip = '34.125.51.194'
                public_url = 'http://{}:{}/images/{}_{}.jpg'.format(public_ip, self.server.server_port, dni,id_participation)

                print('URL pública:', public_url)

                # Procesa los datos según tus necesidades
                # Aquí puedes realizar acciones adicionales si es necesario.
                record = {
                    "dni": dni,
                    "name": name,
                    "photo_url": public_url
                }

                db.collection("moli_records").document(dni + "_" + id_participation).set(record)
                # Envía una respuesta al cliente con la URL pública
                response_data = {'status': 'success', 'message': 'Datos recibidos y procesados correctamente', 'public_url': public_url}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            else:
                # Si falta alguno de los campos requeridos, devuelve un error
                raise ValueError('Se requieren tanto "photo_url" como "code" en los datos JSON.')
        except json.JSONDecodeError as e:
            # Si hay un error al parsear el JSON, devuelve un error
            self.send_error(400, explanation='Error al decodificar el cuerpo JSON: {}'.format(str(e)))

    

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Iniciando servidor en el puerto 8000...')
    httpd.serve_forever()
