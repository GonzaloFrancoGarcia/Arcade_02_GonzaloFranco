#!/usr/bin/env python3
import sys
import threading
import json
import traceback
from datetime import datetime
import os

# Ajuste de path para importar desde la raíz del proyecto
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

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
        print("⚠️ Error al enviar resultado:", e)

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
    # Tamaño del tablero
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    # Configuración de Pygame
    SIZE = 600
    MARGIN = 50
    BOARD = SIZE - 2 * MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + 100))
    pygame.display.set_caption(f"N-Reinas (N={N})")
    font = pygame.font.SysFont(None, 24)
    font_help = pygame.font.SysFont(None, 20)

    queens = set()
    pasos = 0
    solved = False
    solved_time = None

    # IA
    show_help = False
    help_text = ""

    # Botón de Ayuda IA
    button_rect = pygame.Rect(SIZE - 130, SIZE + 35, 120, 30)
    button_color = (70, 130, 180)

    clock = pygame.time.Clock()

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                return

            if evt.type == pygame.MOUSEBUTTONDOWN and not solved:
                x, y = evt.pos

                # Clic en tablero
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

                # Clic en botón Ayuda IA
                if button_rect.collidepoint(x, y):
                    estado = {"reinas": list(queens), "N": N}
                    show_help = True
                    help_text = "Pensando..."
                    def fetch_help():
                        nonlocal help_text
                        try:
                            sugerencia = solicitar_sugerencia("nreinas", estado)
                        except Exception as e:
                            sugerencia = f"Error IA: {e}"
                        help_text = sugerencia
                    threading.Thread(target=fetch_help, daemon=True).start()

        # Dibujar fondo y tablero
        screen.fill((255, 255, 255))
        for r in range(N):
            for c in range(N):
                rect = pygame.Rect(
                    MARGIN + c * CELL, MARGIN + r * CELL,
                    CELL, CELL
                )
                color = (200, 200, 200) if (r + c) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(screen, color, rect)

        # Dibujar reinas
        for (r, c) in queens:
            center = (
                MARGIN + c * CELL + CELL // 2,
                MARGIN + r * CELL + CELL // 2
            )
            pygame.draw.circle(screen, (255, 0, 0), center, CELL // 3)

        # Texto de pasos
        screen.blit(font.render(f"Pasos: {pasos}", True, (0, 0, 0)), (10, SIZE))

        # Mensaje de resuelto
        if solved:
            screen.blit(font.render("¡Resuelto! Enviando resultado...", True, (0, 128, 0)), (MARGIN, SIZE + 5))
            # Cierra tras 2 segundos
            if pygame.time.get_ticks() - solved_time > 2000:
                pygame.quit()
                return

        # Dibujar botón Ayuda IA
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(font_help.render("Ayuda IA", True, (255, 255, 255)),
                    (button_rect.x + 15, button_rect.y + 5))

        # Mostrar respuesta IA
        if show_help:
            # Fondo semitransparente
            help_bg = pygame.Surface((SIZE - 20, 80))
            help_bg.set_alpha(200)
            help_bg.fill((240, 240, 240))
            screen.blit(help_bg, (10, SIZE + 40))
            # Render de hasta 4 líneas
            lines = help_text.split("\n")
            for i, line in enumerate(lines[:4]):
                txt = font_help.render(line, True, (0, 0, 0))
                screen.blit(txt, (20, SIZE + 50 + i * 20))

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        pygame.quit()
