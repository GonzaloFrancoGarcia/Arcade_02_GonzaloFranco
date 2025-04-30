#!/usr/bin/env python3
import json
from clients.common.network import Client

def hanoi(n, origen, destino, auxiliar, moves):
    if n == 0:
        return
    hanoi(n-1, origen, auxiliar, destino, moves)
    moves.append((origen, destino))
    hanoi(n-1, auxiliar, destino, origen, moves)

def main():
    n = int(input("▶️  ¿Cuántos discos? "))
    moves = []
    hanoi(n, 'A', 'C', 'B', moves)
    total = len(moves)
    print(f"🏁 Movimientos mínimos para {n} discos: {total}")
    # Opcional: podrías reproducir la secuencia, aquí solo contamos.

    payload = {
        'juego': 'hanoi',
        'discos': n,
        'movimientos': total,
        'resuelto': True
    }
    Client().send(json.dumps(payload))

if __name__ == '__main__':
    main()
