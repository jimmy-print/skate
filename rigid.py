import pygame
from math import *

from utils import *
from phys import *
utils.debug = True

g_accel = 0.4

fps = 60

def main():
    com = point_mass(300, 300, 10)
    l = line(com, 200)

    l.angle=rad(30)
    l.apply_force(Force(newtons=5, direction=l.angle + rad(90)), distance_from_com=50, color=WHITE)
    l.apply_force(Force(newtons=20, direction=rad(270)), distance_from_com=0, color=WHITE)

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

        #l.apply_force(Force(newtons=l.mass * g_accel, direction=rad(270)), distance_from_com=0, color=WHITE)

        leftmost_point_x = l.center_mass.x - cos(l.angle) * (l.total_length/2)
        leftmost_point_y = l.center_mass.y - sin(l.angle) * (l.total_length/2)
        leftmost_point_rect = pygame.Rect(leftmost_point_x, leftmost_point_y, 1, 1)
        if leftmost_point_rect.colliderect(pygame.Rect(0, -100, D_WIDTH, 100)):
            #l_angular_momentum = l.rotational_inertia * l.angular_velocity
            leftmost_point_velocity = Velocity(l.total_length/2 * l.angular_velocity, l.angle + rad(90 if l.angular_velocity > 0 else 270))
            leftmost_point_velocity = get_net_vector(leftmost_point_velocity, l.center_mass.velocity)
            print(leftmost_point_velocity)
            draw_vector(leftmost_point_velocity, leftmost_point_x, leftmost_point_y, GREEN)
            l.angular_velocity = 0

        pygame.draw.rect(display, BLUE, (0, D_HEIGHT - 1, D_WIDTH, 1))

        l.tick()


        l.draw()

        pygame.display.update()
        clock.tick(fps)

        if frm_by_frm:
            if input() == 'f':
                frm_by_frm = not frm_by_frm

if __name__ == '__main__':
    main()