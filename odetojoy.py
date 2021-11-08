import math
from math import sin, cos, sqrt, acos
from utils import rad, deg
from angular import point_mass, Velocity, display, pygame, BLACK, GREEN, WHITE, axle__, line, point_mass_on_line, Force

axle = axle__(400, 200, 10)
l = line(axle, (
    point_mass_on_line(axle, 200, 10),
    point_mass_on_line(axle, -200, 10)
))

t = 0
frm_by_frm = False

clock = pygame.time.Clock()

while True:
    display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                frm_by_frm = not frm_by_frm

    if 0 < t < 180:
        l.apply_force(Force(-1, rad(deg(l.angle) + 90)), -100)
        l.apply_force(Force(1, rad(90)), 0)

    l.tick()
    l.draw()

    pygame.display.update()
    t += 1

    if frm_by_frm:
        if input() == 'f':
            frm_by_frm = not frm_by_frm

    clock.tick(60)