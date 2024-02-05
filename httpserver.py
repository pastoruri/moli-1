from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        new_path = 'http://%s%s' % (self.headers['Host'], self.path)
        self.send_header('Location', new_path)
        self.end_headers()

server_address = ('localhost', 443)
httpd = HTTPServer(server_address, RedirectHandler)

# Ruta a los certificados SSL para HTTPS
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               certfile='path/to/cert.pem',
                               keyfile='path/to/key.pem',
                               ssl_version=ssl.PROTOCOL_TLS)

print('Servidor corriendo en https://localhost:443')
httpd.serve_forever()
