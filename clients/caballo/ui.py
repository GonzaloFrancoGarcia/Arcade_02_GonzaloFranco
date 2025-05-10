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
N = 8
CELL = (SIZE - 2 * MARGIN) // N

# Globals for IA help
help_text = ""
suggested_move = None    # tuple (r, c)
possible_moves = []      # list of (r, c)

def wrap_text(text, font, max_width):
    """Split `text` into lines that fit within `max_width` pixels."""
    words = text.split(' ')
    lines, current = [], ''
    for w in words:
        test = (current + ' ' + w).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def send_result(start, moves, completed):
    payload = {
        'juego': 'caballo',
        'inicio': start,
        'movimientos': moves,
        'completado': completed,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print(f"⚠️ Error sending result: {e}")

def fetch_help(state):
    global help_text, suggested_move
    try:
        suggestion = solicitar_sugerencia("caballo", state)
    except Exception as e:
        suggestion = f"Error IA: {e}"
    help_text = suggestion
    # parse "(row, col)"
    m = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", suggestion)
    if m:
        suggested_move = (int(m.group(1)) - 1, int(m.group(2)) - 1)
    else:
        suggested_move = None

def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption("Knight’s Tour")
    font = pygame.font.SysFont(None, 20)
    font_h = pygame.font.SysFont(None, 18)

    knight = None
    start = None
    visited = set()
    moves = 0
    solved = False
    solved_time = 0

    global help_text, suggested_move, possible_moves
    help_text = "<waiting for IA>"
    suggested_move = None
    possible_moves = []

    btn = pygame.Rect(SIZE - 120, SIZE + INFO_HEIGHT - 50, 100, 25)
    btn_color = (70, 130, 180)
    clock = pygame.time.Clock()

    offsets = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                x, y = e.pos
                # clear previous highlights
                possible_moves = []
                suggested_move = None

                # click on board
                if not solved and MARGIN <= x < MARGIN + CELL * N and MARGIN <= y < MARGIN + CELL * N:
                    c = (x - MARGIN) // CELL
                    r = (y - MARGIN) // CELL
                    if knight is None:
                        knight = (r, c)
                        start = (r, c)
                        visited.add((r, c))
                    else:
                        dr, dc = r - knight[0], c - knight[1]
                        if (dr, dc) in offsets and (r, c) not in visited:
                            knight = (r, c)
                            visited.add((r, c))
                            moves += 1
                            if len(visited) == N * N:
                                solved = True
                                solved_time = pygame.time.get_ticks()
                                ini_str = f"{chr(start[1]+65)}{start[0]+1}"
                                threading.Thread(
                                    target=send_result,
                                    args=(ini_str, moves, True),
                                    daemon=True
                                ).start()

                # click on IA help button
                if btn.collidepoint(x, y):
                    help_text = "<waiting for IA>"
                    suggested_move = None
                    # compute possible knight moves
                    if knight:
                        for dr, dc in offsets:
                            nr, nc = knight[0] + dr, knight[1] + dc
                            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in visited:
                                possible_moves.append((nr, nc))
                    # call IA
                    state = {
                        "N": N,
                        "inicio": f"{chr(start[1]+65)}{start[0]+1}" if start else None,
                        "visitadas": list(visited)
                    }
                    threading.Thread(target=lambda: fetch_help(state), daemon=True).start()

        # draw board
        screen.fill((255, 255, 255))
        for r in range(N):
            for c in range(N):
                col = (240,240,240) if (r + c) % 2 == 0 else (160,160,160)
                pygame.draw.rect(screen, col, (MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL))

        # draw visited
        for (r, c) in visited:
            pygame.draw.rect(screen, (100,200,100), (MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL))

        # highlight possible moves in yellow
        for (r, c) in possible_moves:
            overlay = pygame.Surface((CELL, CELL))
            overlay.set_alpha(150)
            overlay.fill((255,255,0))
            screen.blit(overlay, (MARGIN + c*CELL, MARGIN + r*CELL))

        # draw knight
        if knight:
            center = (MARGIN + knight[1]*CELL + CELL//2, MARGIN + knight[0]*CELL + CELL//2)
            pygame.draw.circle(screen, (0,0,255), center, CELL//3)

        # highlight IA suggestion
        if suggested_move:
            r, c = suggested_move
            pygame.draw.rect(
                screen, (0,255,0),
                (MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL), 3
            )

        # moves count and solved message
        screen.blit(font.render(f"Moves: {moves}", True, (0,0,0)), (10, SIZE))
        if solved:
            screen.blit(font.render("Completed!", True, (0,128,0)), (MARGIN, SIZE+5))
            if pygame.time.get_ticks() - solved_time > 1500:
                pygame.quit()
                return

        # IA button
        pygame.draw.rect(screen, btn_color, btn)
        screen.blit(font_h.render("IA Help", True, (255,255,255)), (btn.x+10, btn.y+5))

        # help text box
        bg = pygame.Surface((SIZE-20, INFO_HEIGHT))
        bg.set_alpha(200)
        bg.fill((240,240,240))
        screen.blit(bg, (10, SIZE))
        lines = wrap_text(help_text, font_h, SIZE-40)
        for i, line in enumerate(lines[:4]):
            screen.blit(font_h.render(line, True, (0,0,0)), (15, SIZE+5 + i*18))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
