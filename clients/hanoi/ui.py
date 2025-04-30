#!/usr/bin/env python3
import sys
import threading
import json
from datetime import datetime
import traceback

import pygame
from clients.common.network import Client

def send_result(discos, movimientos, resuelto):
    payload = {
        'juego': 'hanoi',
        'discos': discos,
        'movimientos': movimientos,
        'resuelto': resuelto,
        'timestamp': datetime.utcnow().isoformat()
    }
    Client().send(json.dumps(payload))

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    SIZE = 600
    MARGIN = 50
    BASE_Y = SIZE - MARGIN//2
    peg_x = [MARGIN + i*( (SIZE-2*MARGIN)//2 ) for i in range(3)]

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE))
    pygame.display.set_caption("Torres de Hanói")
    font = pygame.font.SysFont(None, 24)

    pegs = {0: list(range(n,0,-1)), 1: [], 2: []}
    movimientos = 0
    selected = None
    solved = False
    solved_time = None

    clock = pygame.time.Clock()

    def draw():
        screen.fill((255,255,255))
        for i,x in enumerate(peg_x):
            pygame.draw.line(screen, (0,0,0), (x, MARGIN), (x, BASE_Y), 5)
            stack = pegs[i]
            for depth, size in enumerate(stack):
                w,h = size*20,20
                rect = pygame.Rect(x-w//2, BASE_Y-(depth+1)*h, w, h)
                pygame.draw.rect(screen, (150,150+size*5,200-size*5), rect)
        screen.blit(font.render(f"Movimientos: {movimientos}", True, (0,0,0)), (10,10))

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return
            if evt.type == pygame.MOUSEBUTTONDOWN and not solved:
                mx,my = evt.pos
                # click cerca de poste
                for i,x in enumerate(peg_x):
                    if abs(mx-x) < 30:
                        if selected is None and pegs[i]:
                            selected = i
                        elif selected is not None:
                            if not pegs[i] or pegs[selected][-1] < pegs[i][-1]:
                                pegs[i].append(pegs[selected].pop())
                                movimientos += 1
                            selected = None
                        break
                # comprobación de fin
                if len(pegs[2]) == n:
                    solved = True
                    solved_time = pygame.time.get_ticks()
                    threading.Thread(
                        target=send_result,
                        args=(n, movimientos, True),
                        daemon=True
                    ).start()

        draw()
        if solved:
            screen.blit(font.render("¡Resuelto! Enviando...", True, (0,128,0)), (MARGIN,10))
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
