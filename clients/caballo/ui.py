#!/usr/bin/env python3
import sys
import threading
import json
import traceback
from datetime import datetime
import os

# Ajuste de path para importar desde la raíz
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

def send_result(inicio, movimientos, completado):
    payload = {
        'juego': 'caballo',
        'inicio': inicio,
        'movimientos': movimientos,
        'completado': completado,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print("⚠️ Error al enviar resultado:", e)

def main():
    N = 8
    SIZE = 600
    INFO_HEIGHT = 100
    MARGIN = 50
    BOARD = SIZE - 2 * MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption("Knight’s Tour")
    font = pygame.font.SysFont(None, 24)
    font_help = pygame.font.SysFont(None, 20)

    knight_pos = None
    start_pos = None
    visited = set()
    movimientos = 0
    solved = False
    solved_time = None

    # IA
    show_help = False
    help_text = ""
    button_rect = pygame.Rect(SIZE - 130, SIZE + INFO_HEIGHT - 65, 120, 30)
    button_color = (70, 130, 180)

    offsets = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
    clock = pygame.time.Clock()

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return

            if evt.type == pygame.MOUSEBUTTONDOWN:
                x,y = evt.pos

                # Clic en tablero
                if not solved and MARGIN <= x < MARGIN+CELL*N and MARGIN <= y < MARGIN+CELL*N:
                    c = (x - MARGIN)//CELL
                    r = (y - MARGIN)//CELL
                    if knight_pos is None:
                        knight_pos = (r,c)
                        start_pos = (r,c)
                        visited.add((r,c))
                    else:
                        dr,dc = r-knight_pos[0], c-knight_pos[1]
                        if (dr,dc) in offsets and (r,c) not in visited:
                            knight_pos = (r,c)
                            visited.add((r,c))
                            movimientos += 1
                            if len(visited) == N*N:
                                solved = True
                                solved_time = pygame.time.get_ticks()
                                inicio_str = f"{chr(start_pos[1]+65)}{start_pos[0]+1}"
                                threading.Thread(
                                    target=send_result,
                                    args=(inicio_str, movimientos, True),
                                    daemon=True
                                ).start()

                # Clic en botón IA
                if button_rect.collidepoint(x,y):
                    estado = {
                        "N": N,
                        "inicio": f"{chr(start_pos[1]+65)}{start_pos[0]+1}" if start_pos else None,
                        "visitadas": [[r,c] for (r,c) in visited]
                    }
                    show_help = True
                    help_text = "Pensando..."
                    def fetch_help():
                        nonlocal help_text
                        try:
                            help_text = solicitar_sugerencia("caballo", estado)
                        except Exception as e:
                            help_text = f"Error IA: {e}"
                    threading.Thread(target=fetch_help, daemon=True).start()

        # Dibujo tablero
        screen.fill((255,255,255))
        for r in range(N):
            for c in range(N):
                rect = pygame.Rect(MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL)
                color = (240,240,240) if (r+c)%2==0 else (160,160,160)
                pygame.draw.rect(screen, color, rect)

        # Casillas visitadas
        for (r,c) in visited:
            rect = pygame.Rect(MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL)
            pygame.draw.rect(screen, (100,200,100), rect)

        # Caballo
        if knight_pos:
            center = (MARGIN+knight_pos[1]*CELL+CELL//2, MARGIN+knight_pos[0]*CELL+CELL//2)
            pygame.draw.circle(screen, (0,0,255), center, CELL//3)

        # Movimientos
        screen.blit(font.render(f"Movimientos: {movimientos}", True, (0,0,0)), (10, SIZE))

        # Resuelto
        if solved:
            screen.blit(font.render("¡Completado! Enviando...", True, (0,128,0)), (MARGIN, SIZE+5))
            if pygame.time.get_ticks() - solved_time > 2000:
                pygame.quit()
                return

        # Botón IA
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(font_help.render("Ayuda IA", True, (255,255,255)),
                    (button_rect.x + 15, button_rect.y + 5))

        # Respuesta IA
        if show_help:
            help_bg = pygame.Surface((SIZE - 20, 80))
            help_bg.set_alpha(200)
            help_bg.fill((240,240,240))
            screen.blit(help_bg, (10, SIZE+40))
            for i, line in enumerate(help_text.split("\n")[:4]):
                txt = font_help.render(line, True, (0,0,0))
                screen.blit(txt, (20, SIZE+50 + i*20))

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        pygame.quit()
