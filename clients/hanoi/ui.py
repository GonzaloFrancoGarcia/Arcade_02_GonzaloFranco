#!/usr/bin/env python3
import sys, threading, json, traceback, os
from datetime import datetime

# Path setup
THIS_DIR=os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT=os.path.abspath(os.path.join(THIS_DIR,os.pardir,os.pardir))
if PROJECT_ROOT not in sys.path: sys.path.insert(0,PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

RULES_HANOI = (
    "- Solo mueve un disco a la vez.\n"
    "- Nunca pongas un disco mayor sobre uno menor.\n"
    "- Objetivo: trasladar todos los discos al tercer poste."
)

def send_result(d,m,ok):
    payload={'juego':'hanoi','discos':d,'movimientos':m,'resuelto':ok,'timestamp':datetime.utcnow().isoformat()}
    try: Client().send(json.dumps(payload))
    except Exception as e: print("⚠️ Error al enviar:",e)

def main():
    n=int(sys.argv[1]) if len(sys.argv)>1 else 3
    SIZE,INFO,M=500,80,40
    BASE=SIZE-M//2

    pygame.init()
    screen=pygame.display.set_mode((SIZE,SIZE+INFO))
    pygame.display.set_caption("Torres de Hanói")
    font=pygame.font.SysFont(None,20); font_h=pygame.font.SysFont(None,18)

    pegs={0:list(range(n,0,-1)),1:[],2:[]}
    mov=0; sel=None; solved=False; st=0
    show=False; help_t=""

    btn=pygame.Rect(SIZE-120,SIZE+INFO-50,100,25); bcol=(70,130,180)
    clock=pygame.time.Clock()

    def draw():
        screen.fill((255,255,255))
        for i in range(3):
            x=M+i*((SIZE-2*M)//2)
            pygame.draw.line(screen,(0,0,0),(x,M),(x,BASE),4)
            for depth,sz in enumerate(pegs[i]):
                w,h=sz*18,18
                pygame.draw.rect(
                    screen,
                    (150,150+sz*5,200-sz*5),
                    pygame.Rect(x-w//2,BASE-(depth+1)*h,w,h)
                )
        screen.blit(font.render(f"Movs: {mov}",True,(0,0,0)),(10,10))

    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();return
            if e.type==pygame.MOUSEBUTTONDOWN:
                x,y=e.pos
                if not solved:
                    for i in range(3):
                        xg=M+i*((SIZE-2*M)//2)
                        if abs(x-xg)<25:
                            if sel is None and pegs[i]: sel=i
                            elif sel is not None:
                                if not pegs[i] or pegs[sel][-1]<pegs[i][-1]:
                                    pegs[i].append(pegs[sel].pop()); mov+=1
                                sel=None
                            break
                    if len(pegs[2])==n:
                        solved=True; st=pygame.time.get_ticks()
                        threading.Thread(target=send_result,args=(n,mov,True),daemon=True).start()
                if btn.collidepoint(x,y):
                    show=True; help_t=RULES_HANOI
                    estado={"discos":n,"pegs":pegs}
                    def f():
                        nonlocal help_t
                        try: help_t=solicitar_sugerencia("hanoi",estado)
                        except Exception as ex: help_t=f"Error IA: {ex}"
                    threading.Thread(target=f,daemon=True).start()

        draw()
        if solved:
            screen.blit(font.render("¡Resuelto!",True,(0,128,0)),(M,BASE+5))
            if pygame.time.get_ticks()-st>1500: pygame.quit();return

        pygame.draw.rect(screen,bcol,btn)
        screen.blit(font_h.render("Ayuda IA",True,(255,255,255)),(btn.x+10,btn.y+5))
        if show:
            bg=pygame.Surface((SIZE-20,60));bg.set_alpha(200);bg.fill((240,240,240))
            screen.blit(bg,(10,SIZE+15))
            for i,line in enumerate(help_t.split("\n")[:3]):
                screen.blit(font_h.render(line,True,(0,0,0)),(15,SIZE+20+i*18))

        pygame.display.flip(); clock.tick(30)

if __name__=='__main__':
    main()
