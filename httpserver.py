from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.redirect()

    def do_POST(self):
        self.redirect()
    
    def do_PUT(self):
        self.redirect()
    
    def do_DELETE(self):
        self.redirect()

    def redirect(self):
        # Cambia "localhost" por tu dominio o dirección IP específica si es necesario
        new_path = f'http://34.125.51.194:8000{self.path}'
        self.send_response(301)
        self.send_header('Location', new_path)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=RedirectHandler, port=443):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    # Configura aquí tu certificado y clave
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile='cert.pem',
                                   keyfile='key.pem',
                                   ssl_version=ssl.PROTOCOL_TLS)

    print(f'Servidor corriendo en https://0.0.0.0:{port} y redirigiendo a http://localhost:8000')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
