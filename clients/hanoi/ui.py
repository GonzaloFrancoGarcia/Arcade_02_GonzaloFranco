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

def send_result(discos, movimientos, resuelto):
    payload = {
        'juego': 'hanoi',
        'discos': discos,
        'movimientos': movimientos,
        'resuelto': resuelto,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print("⚠️ Error al enviar resultado:", e)

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    SIZE = 600
    INFO_HEIGHT = 100
    MARGIN = 50
    BASE_Y = SIZE - MARGIN // 2

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption("Torres de Hanói")
    font = pygame.font.SysFont(None, 24)
    font_help = pygame.font.SysFont(None, 20)

    pegs = {0: list(range(n,0,-1)), 1: [], 2: []}
    movimientos = 0
    selected = None
    solved = False
    solved_time = None

    # IA
    show_help = False
    help_text = ""
    button_rect = pygame.Rect(SIZE - 130, SIZE + INFO_HEIGHT - 65, 120, 30)
    button_color = (70, 130, 180)

    clock = pygame.time.Clock()

    def draw_pegs():
        screen.fill((255,255,255))
        for i in range(3):
            x = MARGIN + i * ((SIZE - 2*MARGIN)//2)
            pygame.draw.line(screen, (0,0,0), (x, MARGIN), (x, BASE_Y), 5)
            for depth, size in enumerate(pegs[i]):
                w, h = size*20, 20
                rect = pygame.Rect(x - w//2, BASE_Y - (depth+1)*h, w, h)
                pygame.draw.rect(screen, (150,150+size*5,200-size*5), rect)
        screen.blit(font.render(f"Mov.: {movimientos}", True, (0,0,0)), (10,10))

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return

            if evt.type == pygame.MOUSEBUTTONDOWN:
                mx, my = evt.pos

                # mover disco
                if not solved:
                    for i in range(3):
                        x = MARGIN + i * ((SIZE - 2*MARGIN)//2)
                        if abs(mx-x) < 30:
                            if selected is None and pegs[i]:
                                selected = i
                            elif selected is not None:
                                if not pegs[i] or pegs[selected][-1] < pegs[i][-1]:
                                    pegs[i].append(pegs[selected].pop())
                                    movimientos += 1
                                selected = None
                            break
                    if len(pegs[2]) == n:
                        solved = True
                        solved_time = pygame.time.get_ticks()
                        threading.Thread(
                            target=send_result,
                            args=(n, movimientos, True),
                            daemon=True
                        ).start()

                # botón IA
                if button_rect.collidepoint(mx,my):
                    estado = {"n": n, "pegs": pegs}
                    show_help = True
                    help_text = "Pensando..."
                    def fetch_help():
                        nonlocal help_text
                        try:
                            help_text = solicitar_sugerencia("hanoi", estado)
                        except Exception as e:
                            help_text = f"Error IA: {e}"
                    threading.Thread(target=fetch_help, daemon=True).start()

        draw_pegs()

        # mensaje resuelto
        if solved:
            screen.blit(font.render("¡Resuelto! Enviando...", True, (0,128,0)), (MARGIN, BASE_Y+10))
            if pygame.time.get_ticks() - solved_time > 2000:
                pygame.quit()
                return

        # botón IA
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(font_help.render("Ayuda IA", True, (255,255,255)),
                    (button_rect.x + 15, button_rect.y + 5))

        # respuesta IA
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
