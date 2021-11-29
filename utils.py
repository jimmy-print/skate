import math
import pygame

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
ORANGE = 255, 165, 0
# PINK = 255, 0, 0
GREY = 125, 125, 125
CYAN = 0, 255, 255
DARKGREY = 25, 25, 25
KINDADARKGREY = 40, 40, 40
MAGENTA = 255, 0, 255

D_WIDTH, D_HEIGHT = 1500, 700
stage_width, stage_height = 1300, 600
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))
debug = False

pygame.font.init()
font = pygame.font.Font("inconsolata.ttf", 15)


def deg(radangle):
    return radangle * 180 / math.pi


def rad(degangle):
    return degangle * (math.pi / 180)


def all_same(items):
    return all(x == items[0] for x in items)


def all_unique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)


def extract_sign(x):
    return x / abs(x)


def norm(radangle):
    degangle = deg(radangle)
    if degangle < 0:
        while degangle < 0:
            degangle += 360
    elif degangle > 360:
        while degangle > 360:
            degangle -= 360
    return rad(degangle)


def close(n, m, min_diff=3):
    return abs(n - m) <= min_diff


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


class tolstoj:
    def __init__(self, loops):
        self.loops = loops
        self.cond = False
        self.i = None

    def do(self):
        self.cond = True
        self.i = 0

    def iter(self):
        try:
            if self.i < self.loops:
                self.cond = True
                self.i += 1
            else:
                self.cond = False
                self.i = None
        except TypeError:
            pass


def in_rect(x, y, rect):
    if (rect.x + rect.width > x > rect.x
        and rect.y + rect.height > y > rect.y):
        return True
    return False


def lighter(c):
    "shitty function"
    return [v + 10 for v in c]
