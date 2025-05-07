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

# Visual params
SIZE = 500
INFO_HEIGHT = 80
MARGIN = 40
BASE_Y = SIZE - MARGIN//2

# Globals
help_text = ""
suggested_rods = None  # tuple (from_idx, to_idx) zero-based

def send_result(d,m,ok):
    payload = {
        'juego': 'hanoi',
        'discos': d,
        'movimientos': m,
        'resuelto': ok,
        'timestamp': datetime.utcnow().isoformat()
    }
    try: Client().send(json.dumps(payload))
    except Exception as e: print("⚠️ Error al enviar:", e)

def fetch_help(estado):
    global help_text, suggested_rods
    try: suggestion = solicitar_sugerencia("hanoi", estado)
    except Exception as e: suggestion = f"Error IA: {e}"
    help_text = suggestion
    m = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", suggestion)
    if m:
        frm = int(m.group(1)) - 1
        to  = int(m.group(2)) - 1
        suggested_rods = (frm, to)
    else:
        suggested_rods = None

def draw_pegs(screen, pegs):
    # dibuja postes y discos
    for i in range(3):
        x = MARGIN + i * ((SIZE-2*MARGIN)//2)
        pygame.draw.line(screen,(0,0,0),(x,MARGIN),(x,BASE_Y),4)
        for depth,sz in enumerate(pegs[i]):
            w,h = sz*18,18
            rect = pygame.Rect(x-w//2, BASE_Y-(depth+1)*h, w, h)
            pygame.draw.rect(screen, (150,150+sz*5,200-sz*5), rect)
    # highlight sugerido
    if suggested_rods:
        for idx,color in zip(suggested_rods, [(0,255,0),(255,255,0)]):
            x = MARGIN + idx * ((SIZE-2*MARGIN)//2)
            overlay = pygame.Surface((40, BASE_Y-MARGIN))
            overlay.set_alpha(100); overlay.fill(color)
            screen.blit(overlay,(x-20, MARGIN))

def main():
    n = int(sys.argv[1]) if len(sys.argv)>1 else 3
    pegs = {0: list(range(n,0,-1)), 1: [], 2: []}
    mov = 0
    sel = None
    solved = False
    solved_time = 0

    global help_text, suggested_rods
    help_text = "<esperando respuesta>"
    suggested_rods = None

    btn = pygame.Rect(SIZE-120, SIZE+INFO_HEIGHT-50, 100,25)
    bcol = (70,130,180)
    clock = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE+INFO_HEIGHT))
    pygame.display.set_caption("Torres de Hanói")
    font = pygame.font.SysFont(None,20)
    font_h = pygame.font.SysFont(None,18)

    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return
            if e.type==pygame.MOUSEBUTTONDOWN:
                x,y = e.pos
                if not solved:
                    # mover disco
                    for i in range(3):
                        xg = MARGIN + i*((SIZE-2*MARGIN)//2)
                        if abs(x-xg)<25:
                            if sel is None and pegs[i]: sel=i
                            elif sel is not None:
                                if not pegs[i] or pegs[sel][-1]<pegs[i][-1]:
                                    pegs[i].append(pegs[sel].pop()); mov+=1
                                sel=None
                            break
                    if len(pegs[2])==n:
                        solved=True; solved_time=pygame.time.get_ticks()
                        threading.Thread(target=send_result,args=(n,mov,True),daemon=True).start()
                if btn.collidepoint(x,y):
                    help_text = "<esperando respuesta>"
                    suggested_rods = None
                    estado = {"discos":n,"pegs":pegs}
                    threading.Thread(target=lambda: fetch_help(estado),daemon=True).start()

        screen.fill((255,255,255))
        draw_pegs(screen, pegs)

        # mov / resuelto
        screen.blit(font.render(f"Movs: {mov}",True,(0,0,0)),(10,10))
        if solved:
            screen.blit(font.render("¡Resuelto!",True,(0,128,0)),(MARGIN,BASE_Y+5))
            if pygame.time.get_ticks()-solved_time>1500: pygame.quit();return

        # botón IA
        pygame.draw.rect(screen,bcol,btn)
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
