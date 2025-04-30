#!/usr/bin/env python3
import sys
import threading
import json
from datetime import datetime
import traceback

import pygame
from clients.common.network import Client

def send_result(inicio, movimientos, completado):
    payload = {
        'juego': 'caballo',
        'inicio': inicio,
        'movimientos': movimientos,
        'completado': completado,
        'timestamp': datetime.utcnow().isoformat()
    }
    Client().send(json.dumps(payload))

def main():
    N = 8
    SIZE = 600
    MARGIN = 50
    BOARD = SIZE - 2 * MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + 50))
    pygame.display.set_caption("Knight’s Tour")
    font = pygame.font.SysFont(None, 24)

    knight_pos = None   # (r, c)
    visited = set()
    movimientos = 0
    solved = False
    offsets = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

    clock = pygame.time.Clock()

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return
            if evt.type == pygame.MOUSEBUTTONDOWN and not solved:
                x, y = evt.pos
                # Dentro del tablero
                if MARGIN <= x < MARGIN + CELL*N and MARGIN <= y < MARGIN + CELL*N:
                    c = (x - MARGIN) // CELL
                    r = (y - MARGIN) // CELL
                    if knight_pos is None:
                        # Primera casilla: posición inicial
                        knight_pos = (r, c)
                        visited.add((r, c))
                    else:
                        # Verificar movimiento legal
                        dr = r - knight_pos[0]
                        dc = c - knight_pos[1]
                        if (dr, dc) in offsets and (r, c) not in visited:
                            knight_pos = (r, c)
                            visited.add((r, c))
                            movimientos += 1
                            # Completado?
                            if len(visited) == N*N:
                                solved = True
                                inicio_pos = f"{chr(list(visited)[0][1]+65)}{list(visited)[0][0]+1}"
                                threading.Thread(
                                    target=send_result,
                                    args=(inicio_pos, movimientos, True),
                                    daemon=True
                                ).start()

        # Dibujar
        screen.fill((255,255,255))
        # Tablero
        for r in range(N):
            for c in range(N):
                rect = pygame.Rect(MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL)
                color = (240,240,240) if (r+c)%2==0 else (160,160,160)
                pygame.draw.rect(screen, color, rect)
        # Visitadas
        for (r,c) in visited:
            rect = pygame.Rect(MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL)
            pygame.draw.rect(screen, (100,200,100), rect)
        # Caballo
        if knight_pos:
            r, c = knight_pos
            center = (MARGIN + c*CELL + CELL//2, MARGIN + r*CELL + CELL//2)
            pygame.draw.circle(screen, (0,0,255), center, CELL//3)
        # Texto
        txt = font.render(f"Movimientos: {movimientos}", True, (0,0,0))
        screen.blit(txt, (10, SIZE))
        if solved:
            msg = font.render("¡Completado! Enviando resultado…", True, (0,128,0))
            screen.blit(msg, (MARGIN, SIZE+10))

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        pygame.quit()

