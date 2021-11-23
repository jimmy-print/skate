import pygame
from math import sin, cos, sqrt, acos
from utils import *
from phys import *

g_accel = 0.7

def main():
    init_axle_x = 100
    init_axle_y = 500
    axle = axle__(init_axle_x, init_axle_y, 10)
    length = 300
    wheels_horz_d = 50
    l = line(
        axle,
        (
            point_mass_on_line(axle, length - wheels_horz_d, 20),
            point_mass_on_line(axle, -wheels_horz_d, 20)
        ),
        wheels_horz_d=wheels_horz_d,
        length=length
    )
    total_horz = abs(l.leftmostpoint.horz) + l.rightmostpoint.horz

    ground_y = 125

    t = 0
    fill = True

    fpsclock = pygame.time.Clock()
    fps_desired = 25
    l.maintain_axle(l.CENT)

    l.apply_force(Force(100, rad(270)), l.rightmostpoint.horz)

    while True:
        display.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        l.apply_force(Force(g_accel * l.mass, rad(270)), 0)



        l.tick()

        if l.rightmostpoint.y <= ground_y:
            l.angular_speed = 0
            l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.rightmostpoint.velocity.magnitude, rad(90)), l.rightmostpoint.horz)

        if l.leftmostpoint.y <= ground_y:
            l.angular_speed = 0
            l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.leftmostpoint.velocity.magnitude, rad(90)), l.leftmostpoint.horz)


        l.draw()

        pygame.draw.line(display, WHITE, (0, D_HEIGHT - ground_y), (D_WIDTH, D_HEIGHT - ground_y))


        pygame.display.update()
        fpsclock.tick(fps_desired)

if __name__ == '__main__':
    main()