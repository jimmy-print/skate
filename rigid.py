import pygame
from math import *

from utils import *
from phys import *
utils.debug = True

g_accel = 0.4

fps = 60

def main():
    l_com = point_mass(300, 300, 10)
    l = line(l_com, 200)

    l.angle=rad(30)
    l.apply_force(Force(newtons=5, direction=l.angle + rad(90)), distance_from_com=50, color=WHITE)
    l.apply_force(Force(newtons=20, direction=rad(0)), distance_from_com=0, color=WHITE)


    j_com = point_mass(x=800, y=250, mass=20)
    j = line(j_com, 300)
    

    clock = pygame.time.Clock()
    frm_by_frm = False
    while True:
        display.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    frm_by_frm = not frm_by_frm

        pygame.draw.rect(display, BLUE, (0, D_HEIGHT - 1, D_WIDTH, 1))

        l.tick()
        j.tick()
        
        l.draw()
        j.draw()

        if line.collide(l, j):
            print('kissing')

        pygame.display.update()
        clock.tick(fps)

        if frm_by_frm:
            if input() == 'f':
                frm_by_frm = not frm_by_frm

if __name__ == '__main__':
    main()
