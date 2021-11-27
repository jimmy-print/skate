import math
import pygame


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

D_WIDTH, D_HEIGHT = 1280, 720
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


pygame.font.init()
font = pygame.font.Font("inconsolata.ttf", 15)

debug = True
