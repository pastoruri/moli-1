import os
import urllib.request
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
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
                public_ip = 'https://e0f0-38-25-17-57.ngrok-free.app'
                public_url = 'http://{}:{}/images/{}_{}.jpg'.format(public_ip, self.server.server_port, dni,id_participation)

                print('URL pública:', public_url)

                # Procesa los datos según tus necesidades
                # Aquí puedes realizar acciones adicionales si es necesario.

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
