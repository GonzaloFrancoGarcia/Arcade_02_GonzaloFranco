#!/usr/bin/env python3
import json
from clients.common.network import Client

# Movimientos legales del caballo
MOVES = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

def knight_tour(N, start):
    board = [[False]*N for _ in range(N)]
    path = []

    def backtrack(r, c, step):
        board[r][c] = True
        path.append((r,c))
        if step == N*N:
            return True
        for dr,dc in MOVES:
            nr, nc = r+dr, c+dc
            if 0 <= nr < N and 0 <= nc < N and not board[nr][nc]:
                if backtrack(nr, nc, step+1):
                    return True
        board[r][c] = False
        path.pop()
        return False

    r0, c0 = start
    found = backtrack(r0, c0, 1)
    return found, len(path)

def pos_to_coord(pos):
    col = ord(pos[0].upper()) - ord('A')
    row = int(pos[1:]) - 1
    return row, col

def main():
    N = 8
    pos = input("▶️  Posición inicial (ej. A1): ")
    start = pos_to_coord(pos)
    print(f"🔍 Buscando Knight’s Tour desde {pos} (esto puede tardar)…")
    completado, movs = knight_tour(N, start)
    print(f"🏁 Completado: {completado}, movimientos: {movs}")

    payload = {
        'juego': 'caballo',
        'inicio': pos.upper(),
        'movimientos': movs,
        'completado': completado
    }
    Client().send(json.dumps(payload))

if __name__ == '__main__':
    main()

