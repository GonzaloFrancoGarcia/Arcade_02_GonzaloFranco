#!/usr/bin/env python3
import sys
import threading
import json
import traceback
from datetime import datetime

import pygame
from clients.common.network import Client

def send_result(N, resuelto, pasos):
    payload = {
        'juego': 'nreinas',
        'N': N,
        'resuelto': resuelto,
        'pasos': pasos,
        'timestamp': datetime.utcnow().isoformat()
    }
    Client().send(json.dumps(payload))

def check_solution(queens, N):
    if len(queens) != N:
        return False
    for (r1, c1) in queens:
        for (r2, c2) in queens:
            if (r1, c1) != (r2, c2):
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    return False
    return True

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    SIZE = 600
    MARGIN = 50
    BOARD = SIZE - 2 * MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + 50))
    pygame.display.set_caption(f"N‑Reinas (N={N})")
    font = pygame.font.SysFont(None, 24)

    queens = set()
    pasos = 0
    solved = False
    solved_time = None

    clock = pygame.time.Clock()

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return
            if evt.type == pygame.MOUSEBUTTONDOWN and not solved:
                x, y = evt.pos
                if MARGIN <= x < MARGIN + CELL * N and MARGIN <= y < MARGIN + CELL * N:
                    c = (x - MARGIN) // CELL
                    r = (y - MARGIN) // CELL
                    if (r, c) in queens:
                        queens.remove((r, c))
                    else:
                        queens.add((r, c))
                    pasos += 1

                    if check_solution(queens, N):
                        solved = True
                        solved_time = pygame.time.get_ticks()
                        threading.Thread(
                            target=send_result, 
                            args=(N, True, pasos),
                            daemon=True
                        ).start()

        # Dibujar tablero y reinas ...
        screen.fill((255,255,255))
        for r in range(N):
            for c in range(N):
                color = (200,200,200) if (r+c)%2==0 else (100,100,100)
                rect = pygame.Rect(MARGIN+c*CELL, MARGIN+r*CELL, CELL, CELL)
                pygame.draw.rect(screen, color, rect)
        for (r,c) in queens:
            center = (MARGIN+c*CELL+CELL//2, MARGIN+r*CELL+CELL//2)
            pygame.draw.circle(screen, (255,0,0), center, CELL//3)

        # Texto pasos
        screen.blit(font.render(f"Pasos: {pasos}", True, (0,0,0)), (10, SIZE))
        # Mensaje resuelto
        if solved:
            screen.blit(font.render("¡Resuelto! Enviando resultado...", True, (0,128,0)), (MARGIN, SIZE+10))
            # Tras 2s cierra
            if pygame.time.get_ticks() - solved_time > 2000:
                pygame.quit()
                return

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        pygame.quit()
