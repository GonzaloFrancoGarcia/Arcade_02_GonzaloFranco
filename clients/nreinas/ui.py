#!/usr/bin/env python3
import sys
import threading
import json
import os
import re
from datetime import datetime

# Path setup so we can import from project root
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
suggested_move = None
conflicts = set()

def wrap_text(text, font, max_width):
    """Split `text` into lines that fit within `max_width` pixels."""
    words = text.split(' ')
    lines, current = [], ''
    for w in words:
        test = f"{current} {w}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def send_result(N, solved, steps):
    payload = {
        'juego': 'nreinas',
        'N': N,
        'resuelto': solved,
        'pasos': steps,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print(f"⚠️ Error sending result: {e}")

def fetch_help(state):
    global help_text, suggested_move, conflicts
    try:
        suggestion = solicitar_sugerencia("nreinas", state)
    except Exception as e:
        suggestion = f"Error IA: {e}"
    help_text = suggestion

    # parse suggested move "(r, c)"
    m = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", suggestion)
    if m:
        suggested_move = (int(m.group(1)) - 1, int(m.group(2)) - 1)
    else:
        suggested_move = None

    # detect conflicts among queens
    queens = {tuple(q) for q in state.get('reinas', [])}
    cset = set()
    for (r1, c1) in queens:
        for (r2, c2) in queens:
            if (r1, c1) != (r2, c2):
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    cset.add((r1, c1))
                    cset.add((r2, c2))
    conflicts = cset

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
    # read N from command line
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    BOARD = SIZE - 2 * MARGIN
    CELL = BOARD // N

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption(f"N-Queens (N={N})")
    font = pygame.font.SysFont(None, 20)
    font_h = pygame.font.SysFont(None, 18)

    queens = set()
    steps = 0
    solved = False
    solved_time = 0

    global help_text, suggested_move, conflicts
    help_text = "<waiting for IA>"
    suggested_move = None
    conflicts = set()

    btn = pygame.Rect(SIZE - 120, SIZE + INFO_HEIGHT - 50, 100, 25)
    btn_color = (70, 130, 180)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.MOUSEBUTTONDOWN and not solved:
                x, y = e.pos
                # clear previous conflicts
                conflicts = set()
                # click on board
                if MARGIN <= x < MARGIN + CELL * N and MARGIN <= y < MARGIN + CELL * N:
                    c = (x - MARGIN) // CELL
                    r = (y - MARGIN) // CELL
                    if (r, c) in queens:
                        queens.remove((r, c))
                    else:
                        queens.add((r, c))
                    steps += 1
                    if check_solution(queens, N):
                        solved = True
                        solved_time = pygame.time.get_ticks()
                        threading.Thread(
                            target=send_result,
                            args=(N, True, steps),
                            daemon=True
                        ).start()
                # click on IA help button
                if btn.collidepoint(x, y):
                    help_text = "<waiting for IA>"
                    suggested_move = None
                    state = {"reinas": list(queens), "N": N}
                    threading.Thread(target=lambda: fetch_help(state), daemon=True).start()

        # draw board
        screen.fill((255, 255, 255))
        for r in range(N):
            for c in range(N):
                col = (200, 200, 200) if (r + c) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(screen, col, (MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL))
        # draw queens
        for (r, c) in queens:
            center = (MARGIN + c*CELL + CELL//2, MARGIN + r*CELL + CELL//2)
            # red if in conflict, else blue
            color = (255, 0, 0) if (r, c) in conflicts else (0, 0, 255)
            pygame.draw.circle(screen, color, center, CELL//3)
        # highlight IA suggestion
        if suggested_move:
            r, c = suggested_move
            pygame.draw.rect(
                screen, (0, 255, 0),
                (MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL), 3
            )

        # draw step count and solved message
        screen.blit(font.render(f"Steps: {steps}", True, (0, 0, 0)), (10, SIZE))
        if solved:
            screen.blit(font.render("Solved!", True, (0, 128, 0)), (MARGIN, SIZE+5))
            if pygame.time.get_ticks() - solved_time > 1500:
                pygame.quit()
                return

        # draw IA button
        pygame.draw.rect(screen, btn_color, btn)
        screen.blit(font_h.render("IA Help", True, (255, 255, 255)), (btn.x+10, btn.y+5))

        # draw IA help text box with wrapping
        bg = pygame.Surface((SIZE-20, INFO_HEIGHT))
        bg.set_alpha(200)
        bg.fill((240, 240, 240))
        screen.blit(bg, (10, SIZE))
        lines = wrap_text(help_text, font_h, SIZE-40)
        for i, line in enumerate(lines[:4]):
            screen.blit(font_h.render(line, True, (0, 0, 0)), (15, SIZE+5 + i*18))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
