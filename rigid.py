import pygame
from math import *

from utils import *
from phys import *
utils.debug = True

g_accel = 0.4

def main():
    com = point_mass(300, 300, 10)
    l = line(com, 200)

    l.apply_force(Force(newtons=0.2, direction=l.angle + rad(90)), distance_from_com=50, color=WHITE)
    l.apply_force(Force(newtons=1, direction=rad(0)), distance_from_com=0, color=WHITE)
    while True:
        display.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        l.draw()
        l.tick()

        pygame.display.update()

if __name__ == '__main__':
    main()