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
BASE_Y = SIZE - MARGIN // 2

# Globals for IA help
help_text = ""
suggested_rods = None    # tuple(origin_idx, dest_idx)
movable_pegs = []        # list of peg indices whose top disk is movable

def wrap_text(text, font, max_width):
    """Split `text` into lines fitting within `max_width` pixels."""
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

def send_result(discs, moves, completed):
    payload = {
        'juego': 'hanoi',
        'discos': discs,
        'movimientos': moves,
        'resuelto': completed,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        Client().send(json.dumps(payload))
    except Exception as e:
        print(f"⚠️ Error sending result: {e}")

def fetch_help(state):
    global help_text, suggested_rods
    try:
        suggestion = solicitar_sugerencia("hanoi", state)
    except Exception as e:
        suggestion = f"Error IA: {e}"
    help_text = suggestion
    # parse "(from, to)"
    m = re.search(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", suggestion)
    if m:
        frm = int(m.group(1)) - 1
        to  = int(m.group(2)) - 1
        suggested_rods = (frm, to)
    else:
        suggested_rods = None

def draw_pegs(screen, pegs):
    spacing = (SIZE - 2*MARGIN) // 2
    # draw poles and disks
    for i in range(3):
        x = MARGIN + i * spacing
        pygame.draw.line(screen, (0,0,0), (x, MARGIN), (x, BASE_Y), 4)
        for depth, size in enumerate(pegs[i]):
            w, h = size * 18, 18
            rect = pygame.Rect(x - w//2,
                               BASE_Y - (depth+1)*h,
                               w, h)
            pygame.draw.rect(screen,
                             (150, 150 + size*5, 200 - size*5),
                             rect)
    # highlight movable top disks in blue
    for peg_idx in movable_pegs:
        if pegs[peg_idx]:
            depth = len(pegs[peg_idx]) - 1
            size = pegs[peg_idx][depth]
            w, h = size * 18, 18
            x = MARGIN + peg_idx * spacing
            rect = pygame.Rect(x - w//2,
                               BASE_Y - (depth+1)*h,
                               w, h)
            overlay = pygame.Surface((w, h))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 255))
            screen.blit(overlay, rect.topleft)
    # highlight suggested move: origin green, dest yellow
    if suggested_rods:
        origin, dest = suggested_rods
        # origin disk border
        if pegs[origin]:
            depth = len(pegs[origin]) - 1
            size = pegs[origin][depth]
            w, h = size * 18, 18
            x0 = MARGIN + origin * spacing
            rect_o = pygame.Rect(x0 - w//2,
                                 BASE_Y - (depth+1)*h,
                                 w, h)
            pygame.draw.rect(screen, (0,255,0), rect_o, 3)
        # destination slot border
        depth2 = len(pegs[dest])
        # assume moving top from origin if exists
        size2 = pegs[origin][-1] if pegs[origin] else 1
        w2, h2 = size2 * 18, 18
        x1 = MARGIN + dest * spacing
        rect_d = pygame.Rect(x1 - w2//2,
                             BASE_Y - (depth2+1)*h2,
                             w2, h2)
        pygame.draw.rect(screen, (255,255,0), rect_d, 3)

def main():
    # initial state
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    pegs = {0: list(range(n,0,-1)), 1: [], 2: []}
    moves = 0
    sel = None
    solved = False
    solved_time = 0

    global help_text, suggested_rods, movable_pegs
    help_text = "<waiting for IA>"
    suggested_rods = None
    movable_pegs = []

    btn = pygame.Rect(SIZE - 120, SIZE + INFO_HEIGHT - 50, 100, 25)
    btn_color = (70,130,180)

    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE + INFO_HEIGHT))
    pygame.display.set_caption("Towers of Hanoi")
    font = pygame.font.SysFont(None, 20)
    font_h = pygame.font.SysFont(None, 18)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                x,y = e.pos
                # clear previous highlights
                suggested_rods = None
                movable_pegs = []
                # regular move logic
                if not solved:
                    for i in range(3):
                        xg = MARGIN + i * ((SIZE-2*MARGIN)//2)
                        if abs(x - xg) < 25:
                            if sel is None and pegs[i]:
                                sel = i
                            elif sel is not None:
                                if not pegs[i] or pegs[sel][-1] < pegs[i][-1]:
                                    pegs[i].append(pegs[sel].pop())
                                    moves += 1
                                sel = None
                            break
                    if len(pegs[2]) == n:
                        solved = True
                        solved_time = pygame.time.get_ticks()
                        threading.Thread(
                            target=send_result,
                            args=(n, moves, True),
                            daemon=True
                        ).start()
                # IA help button
                if btn.collidepoint(x,y):
                    help_text = "<waiting for IA>"
                    # compute movable pegs
                    for i in range(3):
                        if pegs[i]:
                            top = pegs[i][-1]
                            for j in range(3):
                                if j != i and (not pegs[j] or top < pegs[j][-1]):
                                    movable_pegs.append(i)
                                    break
                    # call IA
                    state = {"discos": n, "pegs": pegs}
                    threading.Thread(target=lambda: fetch_help(state), daemon=True).start()

        screen.fill((255,255,255))
        draw_pegs(screen, pegs)

        # moves count and solved
        screen.blit(font.render(f"Moves: {moves}", True, (0,0,0)), (10,10))
        if solved:
            screen.blit(font.render("Completed!", True, (0,128,0)), (MARGIN, BASE_Y+5))
            if pygame.time.get_ticks() - solved_time > 1500:
                pygame.quit()
                return

        # draw IA button
        pygame.draw.rect(screen, btn_color, btn)
        screen.blit(font_h.render("IA Help", True, (255,255,255)), (btn.x+10, btn.y+5))

        # draw IA help text box with wrapping
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
