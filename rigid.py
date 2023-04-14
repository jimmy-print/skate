import pygame
from math import *

from utils import *
from phys import *
utils.debug = True

g_accel = 0.4

fps = 60

def main():
    l_com = point_mass(200, D_HEIGHT - 200, 10)
    l = line(l_com, 200)

    l.angle=rad(30)
    l.apply_force(Force(newtons=5, direction=l.angle + rad(90)), distance_from_com=50, color=WHITE)
    l.apply_force(Force(newtons=20, direction=rad(340)), distance_from_com=0, color=WHITE)


    j_com = point_mass(x=D_WIDTH - 300, y=250, mass=20)
    j = line(j_com, 300, PINK)
    j.apply_force(Force(newtons=40, direction=rad(170)), distance_from_com=0, color=WHITE)


    clock = pygame.time.Clock()
    frm_by_frm = False

    frame = 0

    while True:
        frame += 1
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

        '''
        l.center_mass.x = pygame.mouse.get_pos()[0]
        l.center_mass.y = D_HEIGHT - pygame.mouse.get_pos()[1]
        '''
        
        l.draw()
        j.draw()

        
        if 0 < deg(norm(l.angle)) < 180:
            utils.draw_text("right side up", 1, 1)
        elif 180 < deg(norm(l.angle)) < 360:
            utils.draw_text("upside down", 1, 1)
        else:
            raise InTheMiddleException

        collide_result = line.collide(l, j)
        # NOTE: when l is vertical, line.collide returns false
        # prob due to infinite slope breaking something
        if collide_result:
            abs_collision_point_x, abs_collision_point_y = collide_result
            line.docollision(l, j, abs_collision_point_x, abs_collision_point_y)

        pygame.display.update()
        clock.tick(fps)

        if frm_by_frm:
            if input() == 'f':
                frm_by_frm = not frm_by_frm

if __name__ == '__main__':
    main()
