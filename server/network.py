import socket
import threading
import json

from db import init_db, SessionLocal
from models import ReinasResult, CaballoResult, HanoiResult

class Server:
    def __init__(self, host='127.0.0.1', port=5000):
        # Inicializa la base de datos (crea tablas si no existen)
        init_db()

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

    def handle_client(self, conn, addr):
        print(f'🌐 Conexión entrante desde {addr}')
        try:
            data = conn.recv(4096)
            text = data.decode()
            print(f'📨 Recibido raw: {text}')

            # Intentamos parsear JSON
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as e:
                print(f'⚠️ JSON inválido: {e}')
                conn.sendall(b'NACK')
                return

            juego = payload.get('juego')
            sess = SessionLocal()

            if juego == 'nreinas':
                resultado = ReinasResult(
                    N=payload['N'],
                    resuelto=payload['resuelto'],
                    pasos=payload['pasos']
                )
                sess.add(resultado)
                sess.commit()
                print(f'✅ Guardado N‑Reinas: N={payload["N"]}, pasos={payload["pasos"]}')
                conn.sendall(b'ACK')

            elif juego == 'caballo':
                resultado = CaballoResult(
                    inicio=payload['inicio'],
                    movimientos=payload['movimientos'],
                    completado=payload['completado']
                )
                sess.add(resultado)
                sess.commit()
                print(f'✅ Guardado Knight’s Tour: inicio={payload["inicio"]}, movimientos={payload["movimientos"]}')
                conn.sendall(b'ACK')

            elif juego == 'hanoi':
                resultado = HanoiResult(
                    discos=payload['discos'],
                    movimientos=payload['movimientos'],
                    resuelto=payload['resuelto']
                )
                sess.add(resultado)
                sess.commit()
                print(f'✅ Guardado Hanói: discos={payload["discos"]}, movimientos={payload["movimientos"]}, resuelto={payload["resuelto"]}')
                conn.sendall(b'ACK')

            else:
                print(f'ℹ️ Juego no soportado: {juego}')
                conn.sendall(b'NACK')

            sess.close()

        except Exception as e:
            print(f'⚠️ Error manejando cliente {addr}: {e}')
            conn.sendall(b'NACK')
        finally:
            conn.close()

    def start(self):
        print(f'🚀 Servidor escuchando en {self.host}:{self.port}')
        try:
            while True:
                conn, addr = self.sock.accept()
                t = threading.Thread(target=self.handle_client, args=(conn, addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            print('\n🛑 Servidor detenido por teclado')
        finally:
            self.sock.close()

if __name__ == '__main__':
    Server().start()
