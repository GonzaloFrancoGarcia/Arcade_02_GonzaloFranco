#!/usr/bin/env python3
import sys
import threading
import json
import os
import re
from datetime import datetime

# Path setup
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

# Visual parameters
SIZE = 500
INFO_HEIGHT = 80
MARGIN = 40

# Globals for IA help
help_text = ""
suggested_move = None  # tuple (r, c) zero-based

def send_result(N, resuelto, pasos):
    payload = {
        'juego': 'nreinas',
        'N': N,
        'resuelto': resuelto,
        'pasos': pasos,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print(f"⚠️ Error al enviar resultado: {e}")

def fetch_help(estado):
    global help_text, suggested_move
    try:
        suggestion = solicitar_sugerencia("nreinas", estado)
    except Exception as e:
        suggestion = f"Error IA: {e}"
    help_text = suggestion
    # parse "(fila, columna)" base 1
    m = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", suggestion)
    if m:
        r = int(m.group(1)) - 1
        c = int(m.group(2)) - 1
        suggested_move = (r, c)
    else:
        suggested_move = None

def check_solution(queens, N):
    if len(queens) != N:
        return False
    for (r1, c1) in queens:
        for (r2, c2) in queens:
            if (r1, c1) != (r2, c2) and (r1==r2 or c1==c2 or abs(r1-r2)==abs(c1-c2)):
                return False
    return True

def main():
    N = int(sys.argv[1]) if len(sys.argv)>1 else 8
    BOARD = SIZE - 2*MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption(f"N-Reinas (N={N})")
    font = pygame.font.SysFont(None, 20)
    font_h = pygame.font.SysFont(None, 18)

    queens = set()
    pasos = 0
    solved = False
    solved_time = 0

    global help_text, suggested_move
    help_text = "<esperando respuesta>"
    suggested_move = None

    btn = pygame.Rect(SIZE-120, SIZE+INFO_HEIGHT-50, 100,25)
    btn_color = (70,130,180)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN and not solved:
                x,y = e.pos
                # tablero
                if MARGIN<=x<MARGIN+CELL*N and MARGIN<=y<MARGIN+CELL*N:
                    c = (x-MARGIN)//CELL; r = (y-MARGIN)//CELL
                    if (r,c) in queens: queens.remove((r,c))
                    else: queens.add((r,c))
                    pasos += 1
                    if check_solution(queens,N):
                        solved=True; solved_time=pygame.time.get_ticks()
                        threading.Thread(target=send_result, args=(N,True,pasos), daemon=True).start()
                # ayuda IA
                if btn.collidepoint(x,y):
                    help_text = "<esperando respuesta>"
                    suggested_move = None
                    estado = {"reinas":list(queens),"N":N}
                    threading.Thread(target=lambda: fetch_help(estado), daemon=True).start()

        screen.fill((255,255,255))
        # tablero
        for r in range(N):
            for c in range(N):
                col = (200,200,200) if (r+c)%2==0 else (100,100,100)
                pygame.draw.rect(screen, col, (MARGIN+c*CELL, MARGIN+r*CELL, CELL, CELL))
        # reinas
        for (r,c) in queens:
            ctr = (MARGIN+c*CELL+CELL//2, MARGIN+r*CELL+CELL//2)
            pygame.draw.circle(screen, (255,0,0), ctr, CELL//3)
        # highlight sugerido
        if suggested_move:
            r,c = suggested_move
            pygame.draw.rect(
                screen, (0,255,0),
                (MARGIN+c*CELL, MARGIN+r*CELL, CELL, CELL), 3
            )

        # pasos / resuelto
        screen.blit(font.render(f"Pasos: {pasos}",True,(0,0,0)),(10,SIZE))
        if solved:
            screen.blit(font.render("¡Resuelto!",True,(0,128,0)),(MARGIN,SIZE+5))
            if pygame.time.get_ticks()-solved_time>1500:
                pygame.quit();return

        # botón IA
        pygame.draw.rect(screen, btn_color, btn)
        screen.blit(font_h.render("Ayuda IA",True,(255,255,255)),(btn.x+10,btn.y+5))
        # caja IA
        bg = pygame.Surface((SIZE-20,60)); bg.set_alpha(200); bg.fill((240,240,240))
        screen.blit(bg,(10,SIZE+15))
        for i,line in enumerate(help_text.split("\n")[:3]):
            screen.blit(font_h.render(line,True,(0,0,0)),(15,SIZE+20+i*18))

        pygame.display.flip()
        clock.tick(30)

if __name__=='__main__':
    main()
