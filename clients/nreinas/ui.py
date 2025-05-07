#!/usr/bin/env python3
import sys
import threading
import json
import os
from datetime import datetime

# Ajuste de path para importar desde la raíz del proyecto
this_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(this_dir, os.pardir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pygame
from clients.common.network import Client
from clients.common.ia_client import solicitar_sugerencia

# Parámetros visuales
SIZE = 500
INFO_HEIGHT = 80
MARGIN = 40

# Variable global para el texto de ayuda IA
global_help_text = ""

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

# Hilo para consultar IA y actualizar el texto de ayuda
def fetch_help(estado):
    global global_help_text
    try:
        suggestion = solicitar_sugerencia("nreinas", estado)
    except Exception as e:
        suggestion = f"Error IA: {e}"
    global_help_text = suggestion

# Función para chequear solución
def check_solution(queens, N):
    if len(queens) != N:
        return False
    for (r1, c1) in queens:
        for (r2, c2) in queens:
            if (r1, c1) != (r2, c2) and (r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2)):
                return False
    return True

# Función principal
def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    BOARD_SIZE = SIZE - 2 * MARGIN
    CELL = BOARD_SIZE // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption(f"N-Reinas (N={N})")
    font = pygame.font.SysFont(None, 20)
    font_help = pygame.font.SysFont(None, 18)

    queens = set()
    pasos = 0
    solved = False
    solved_time = 0

    show_help = False
    global global_help_text
    global_help_text = "<esperando respuesta>"

    # Rectángulo del botón IA
    btn_rect = pygame.Rect(SIZE - 120, SIZE + INFO_HEIGHT - 50, 100, 25)
    btn_color = (70, 130, 180)

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
                # Clic en botón IA
                if btn_rect.collidepoint(x, y):
                    show_help = True
                    global_help_text = "<esperando respuesta>"
                    estado = {"reinas": list(queens), "N": N}
                    threading.Thread(target=lambda: fetch_help(estado), daemon=True).start()

        # Dibujado
        screen.fill((255, 255, 255))
        # Tablero
        for r in range(N):
            for c in range(N):
                col = (200, 200, 200) if (r + c) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(
                    screen,
                    col,
                    (MARGIN + c * CELL, MARGIN + r * CELL, CELL, CELL)
                )
        # Reinas
        for (r, c) in queens:
            center = (
                MARGIN + c * CELL + CELL // 2,
                MARGIN + r * CELL + CELL // 2
            )
            pygame.draw.circle(screen, (255, 0, 0), center, CELL // 3)

        # Pasos
        screen.blit(font.render(f"Pasos: {pasos}", True, (0, 0, 0)), (10, SIZE))
        # Mensaje de resuelto
        if solved:
            screen.blit(
                font.render("¡Resuelto!", True, (0, 128, 0)),
                (MARGIN, SIZE + 5)
            )
            if pygame.time.get_ticks() - solved_time > 1500:
                pygame.quit()
                return

        # Botón IA
        pygame.draw.rect(screen, btn_color, btn_rect)
        screen.blit(
            font_help.render("Ayuda IA", True, (255, 255, 255)),
            (btn_rect.x + 10, btn_rect.y + 5)
        )

        # Caja de ayuda IA
        if show_help:
            bg = pygame.Surface((SIZE - 20, 60))
            bg.set_alpha(200)
            bg.fill((240, 240, 240))
            screen.blit(bg, (10, SIZE + 15))
            lines = global_help_text.split("\n")
            if not any(line.strip() for line in lines):
                lines = ["<sin sugerencia disponible>"]
            for i, line in enumerate(lines[:3]):
                screen.blit(
                    font_help.render(line, True, (0, 0, 0)),
                    (15, SIZE + 20 + i * 18)
                )

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()
