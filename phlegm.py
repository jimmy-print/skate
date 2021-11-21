import math
from math import sin, cos, sqrt, acos
from utils import rad, deg, close
from angular import point_mass, Velocity, display, pygame, BLACK, GREEN, WHITE, axle__, line, point_mass_on_line, Force, \
    draw_text, D_WIDTH, D_HEIGHT, g_accel

frm_by_frm = False

init_axle_x = 600
init_axle_y = 150
axle = axle__(init_axle_x, init_axle_y, 10)
wheels_horz_d = 100
l = line(axle, (
    point_mass_on_line(axle, 500, 20),
    point_mass_on_line(axle, -200, 20)
))
total_horz = abs(l.leftmostpoint.horz) + l.rightmostpoint.horz
t = 0
clock = pygame.time.Clock()

while True:
    display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                frm_by_frm = not frm_by_frm

    l.apply_force(Force(10, rad(90)), 500)
    l.apply_force(Force(10, rad(90)), -200)
    l.tick()
    l.draw()

    pygame.display.update()
    t += 1

    if frm_by_frm:
        if input() == 'f':
            frm_by_frm = not frm_by_frm

    clock.tick(60)