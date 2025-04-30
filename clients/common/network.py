import socket

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port

    def send(self, message: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(message.encode())
            resp = sock.recv(1024)
            print(f'✅ Respuesta del servidor: {resp.decode()}')

