#!/usr/bin/env python3
import sys, threading, json, traceback, os
from datetime import datetime

# Path setup
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

RULES_NREINAS = (
    "- Coloca N reinas en un tablero de N×N.\n"
    "- Ninguna reina puede atacar a otra: no comparten fila,\n"
    "  columna ni diagonal."
)

def send_result(N, resuelto, pasos):
    payload = {
        'juego':'nreinas','N':N,'resuelto':resuelto,
        'pasos':pasos,'timestamp':datetime.utcnow().isoformat()
    }
    try: Client().send(json.dumps(payload))
    except Exception as e: print("⚠️ Error al enviar resultado:", e)

def check_solution(queens, N):
    if len(queens)!=N: return False
    for (r1,c1) in queens:
        for (r2,c2) in queens:
            if (r1,c1)!=(r2,c2) and (r1==r2 or c1==c2 or abs(r1-r2)==abs(c1-c2)):
                return False
    return True

def main():
    N = int(sys.argv[1]) if len(sys.argv)>1 else 8
    SIZE, INFO, M = 500, 80, 40
    BOARD = SIZE - 2*M
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE+INFO))
    pygame.display.set_caption(f"N-Reinas (N={N})")
    font = pygame.font.SysFont(None,20)
    font_h = pygame.font.SysFont(None,18)

    queens=set(); pasos=0; solved=False; st=0
    show_help=False; help_text=""

    btn = pygame.Rect(SIZE-120, SIZE+INFO-50, 100,25)
    bcol=(70,130,180)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();return
            if e.type==pygame.MOUSEBUTTONDOWN and not solved:
                x,y = e.pos
                # colocación de reinas
                if M<=x<M+CELL*N and M<=y<M+CELL*N:
                    c=(x-M)//CELL; r=(y-M)//CELL
                    if (r,c) in queens: queens.remove((r,c))
                    else: queens.add((r,c))
                    pasos+=1
                    if check_solution(queens,N):
                        solved=True; st=pygame.time.get_ticks()
                        threading.Thread(
                            target=send_result, args=(N,True,pasos), daemon=True
                        ).start()
                # ayuda IA
                if btn.collidepoint(x,y):
                    show_help=True
                    help_text = RULES_NREINAS
                    estado = {"reinas":list(queens),"N":N}
                    def fetch():
                        nonlocal help_text
                        try: help_text = solicitar_sugerencia("nreinas", estado)
                        except Exception as ex: help_text = f"Error IA: {ex}"
                    threading.Thread(target=fetch,daemon=True).start()

        # dibujo
        screen.fill((255,255,255))
        # tablero
        for r in range(N):
            for c in range(N):
                col=(200,200,200) if (r+c)%2==0 else (100,100,100)
                pygame.draw.rect(
                    screen, col,
                    (M+c*CELL, M+r*CELL, CELL, CELL)
                )
        # reinas
        for (r,c) in queens:
            center=(M+c*CELL+CELL//2, M+r*CELL+CELL//2)
            pygame.draw.circle(screen,(255,0,0),center,CELL//3)
        # pasos / resuelto
        screen.blit(font.render(f"Pasos: {pasos}",True,(0,0,0)),(10,SIZE))
        if solved:
            screen.blit(font.render("¡Resuelto!",True,(0,128,0)),(M,SIZE+5))
            if pygame.time.get_ticks()-st>1500:
                pygame.quit();return
        # botón IA
        pygame.draw.rect(screen,bcol,btn)
        screen.blit(font_h.render("Ayuda IA",True,(255,255,255)),(btn.x+10,btn.y+5))
        # caja ayuda
        if show_help:
            bg=pygame.Surface((SIZE-20,60)); bg.set_alpha(200); bg.fill((240,240,240))
            screen.blit(bg,(10,SIZE+15))
            for i,line in enumerate(help_text.split("\n")[:3]):
                screen.blit(font_h.render(line,True,(0,0,0)),(15,SIZE+20+i*18))

        pygame.display.flip(); clock.tick(30)

if __name__=='__main__':
    main()
