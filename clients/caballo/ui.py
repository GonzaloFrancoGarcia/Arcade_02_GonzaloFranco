#!/usr/bin/env python3
import sys, threading, json, traceback, os
from datetime import datetime

# Path setup
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path: sys.path.insert(0,PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

RULES_CABALLO = (
    "- Mueve el caballo en L: 2 casillas en una dirección y 1 en perpendicular.\n"
    "- Debes visitar cada casilla exactamente una vez sin repetir."
)

def send_result(inicio,movs,comp):
    payload={'juego':'caballo','inicio':inicio,'movimientos':movs,'completado':comp,'timestamp':datetime.utcnow().isoformat()}
    try: Client().send(json.dumps(payload))
    except Exception as e: print("⚠️ Error al enviar:",e)

def main():
    N=8; SIZE=500; INFO=80; M=40; CELL=(SIZE-2*M)//N
    pygame.init()
    screen=pygame.display.set_mode((SIZE,SIZE+INFO))
    pygame.display.set_caption("Knight’s Tour")
    font=pygame.font.SysFont(None,20); font_h=pygame.font.SysFont(None,18)

    knight=None; start=None; visited=set()
    movs=0; solved=False; st=0
    show=False; help_t=""

    btn=pygame.Rect(SIZE-120,SIZE+INFO-50,100,25); bcol=(70,130,180)
    offs=[(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
    clock=pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();return
            if e.type==pygame.MOUSEBUTTONDOWN:
                x,y=e.pos
                if not solved and M<=x<M+CELL*N and M<=y<M+CELL*N:
                    c=(x-M)//CELL; r=(y-M)//CELL
                    if knight is None:
                        knight=(r,c); start=(r,c); visited.add((r,c))
                    else:
                        dr,dc=r-knight[0],c-knight[1]
                        if (dr,dc) in offs and (r,c) not in visited:
                            knight=(r,c); visited.add((r,c)); movs+=1
                            if len(visited)==N*N:
                                solved=True; st=pygame.time.get_ticks()
                                ini=f"{chr(start[1]+65)}{start[0]+1}"
                                threading.Thread(target=send_result,args=(ini,movs,True),daemon=True).start()
                if btn.collidepoint(x,y):
                    show=True; help_t=RULES_CABALLO
                    estado={"inicio":f"{chr(start[1]+65)}{start[0]+1}" if start else None,"visitadas":list(visited)}
                    def f(): 
                        nonlocal help_t
                        try: help_t=solicitar_sugerencia("caballo",estado)
                        except Exception as ex: help_t=f"Error IA: {ex}"
                    threading.Thread(target=f,daemon=True).start()

        screen.fill((255,255,255))
        # tablero
        for r in range(N):
            for c in range(N):
                col=(240,240,240) if (r+c)%2==0 else (160,160,160)
                pygame.draw.rect(screen,col,(M+c*CELL,M+r*CELL,CELL,CELL))
        # visitadas
        for (r,c) in visited:
            pygame.draw.rect(screen,(100,200,100),(M+c*CELL,M+r*CELL,CELL,CELL))
        # caballo
        if knight:
            ctr=(M+knight[1]*CELL+CELL//2,M+knight[0]*CELL+CELL//2)
            pygame.draw.circle(screen,(0,0,255),ctr,CELL//3)
        # texto/ resuelto
        screen.blit(font.render(f"Movs: {movs}",True,(0,0,0)),(10,SIZE))
        if solved:
            screen.blit(font.render("¡Completado!",True,(0,128,0)),(M,SIZE+5))
            if pygame.time.get_ticks()-st>1500: pygame.quit();return
        # botón IA
        pygame.draw.rect(screen,bcol,btn)
        screen.blit(font_h.render("Ayuda IA",True,(255,255,255)),(btn.x+10,btn.y+5))
        # caja
        if show:
            bg=pygame.Surface((SIZE-20,60));bg.set_alpha(200);bg.fill((240,240,240))
            screen.blit(bg,(10,SIZE+15))
            for i,line in enumerate(help_t.split("\n")[:3]):
                screen.blit(font_h.render(line,True,(0,0,0)),(15,SIZE+20+i*18))

        pygame.display.flip(); clock.tick(30)

if __name__=='__main__':
    main()
