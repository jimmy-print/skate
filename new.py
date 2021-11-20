import math
from math import sin, cos, sqrt, acos
from utils import rad, deg, close
from angular import point_mass, Velocity, display, pygame, BLACK, GREEN, WHITE, axle__, line, point_mass_on_line, Force, \
    draw_text, D_WIDTH, D_HEIGHT, g_accel
g_accel = 0.8
axle = axle__(200, 150, 10)
l = line(axle, (
    point_mass_on_line(axle, 450, 10),
    point_mass_on_line(axle, -100, 10)
))

t = 0

pausing_this_frm = False

fpsclock = pygame.time.Clock()
fps_desired = 30

done = False
trace = False

def pause():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                quit()

while True:
    pausing_this_frm = False
    if not trace:
        display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pausing_this_frm = True
            if event.key == pygame.K_ESCAPE:
                quit()
            if event.key == pygame.K_q:
                trace = not trace

    if 0 < t < 20:
        l.apply_force(Force(20, 0), 0)
        pass
    if 20 < t < 23:
        l.apply_force(Force(2000, rad(270)), l.leftmostpoint.horz)

    if l.leftmostpoint.y < 100 and not done:
        draw_text('NO HAY QUE HAY QUE HAYMARKEY QUE RRASKOLNIKOF', 500, 500)
        paradox = l.rightmostpoint.velocity
        wittgensteinpopper = l.leftmostpoint.velocity
        watchtower = l.axle.velocity
        done = True
        l.move_axle(175, -275, 275)
        l.angular_speed = 0
        l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0)
        l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0)
        l.apply_force(Force(l.mass * paradox.magnitude / 5, paradox.direction), l.rightmostpoint.horz)
    if done:
        l.apply_force(Force(g_accel * l.mass, rad(270)), 0)
    if 25 < t < 40:
        l.apply_force(Force(50, l.angle + rad(270)), l.rightmostpoint.horz - 100)
        pass

    l.tick()
    l.draw()

    draw_text(f't={t}', 100, 100)

    pygame.draw.line(display, WHITE, (0, D_HEIGHT - 100), (D_WIDTH, D_HEIGHT - 100))
    pygame.draw.polygon(display, WHITE, (
        (l.leftmostpoint.x + math.cos(l.angle) * 100, D_HEIGHT - (l.leftmostpoint.y + math.sin(l.angle) * 150)),
        (l.leftmostpoint.x + math.cos(l.angle) * 100 - 25,
         D_HEIGHT - (l.leftmostpoint.y + math.sin(l.angle) * 150 - 50)),
        (l.leftmostpoint.x + math.cos(l.angle) * 100 + 25,
         D_HEIGHT - (l.leftmostpoint.y + math.sin(l.angle) * 150 - 50))), width=2)
    

    pygame.display.update()
    t += 1

    if pausing_this_frm:
        draw_text('Paused', 200, 80)
        pygame.display.update()
        pause()

    fpsclock.tick(fps_desired)
