#!/usr/bin/env python3
import json
from datetime import datetime
from clients.common.network import Client

def solve_n_reinas(N):
    """
    Encuentra UNA solución al problema de N reinas y cuenta los intentos (pasos).
    Devuelve (resuelto:boolean, pasos:int).
    """
    pasos = 0
    col = set()
    diag1 = set()
    diag2 = set()
    board = [-1] * N
    encontrado = False

    def backtrack(row):
        nonlocal pasos, encontrado
        if encontrado:
            return
        pasos += 1
        if row == N:
            encontrado = True
            return
        for c in range(N):
            if c in col or (row - c) in diag1 or (row + c) in diag2:
                continue
            # Coloco reina
            board[row] = c
            col.add(c); diag1.add(row - c); diag2.add(row + c)
            backtrack(row + 1)
            if encontrado:
                return
            # Deshago
            col.remove(c); diag1.remove(row - c); diag2.remove(row + c)

    backtrack(0)
    return encontrado, pasos

def main():
    N = int(input("▶️  Introduce tamaño de tablero N: "))
    print(f"🔍 Resolviendo N‑Reinas para N={N}...")
    resuelto, pasos = solve_n_reinas(N)
    print(f"🏁 Resuelto: {resuelto} en {pasos} pasos")

    payload = {
        'juego': 'nreinas',
        'N': N,
        'resuelto': resuelto,
        'pasos': pasos,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Envía al servidor
    client = Client()
    client.send(json.dumps(payload))

if __name__ == '__main__':
    main()
