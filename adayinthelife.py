import math
from math import sin, cos, sqrt, acos
from utils import rad, deg
from angular import point_mass, Velocity, display, pygame, BLACK, GREEN, WHITE, D_HEIGHT, D_WIDTH, RED, draw_vector, YELLOW, get_net_vector

angle = rad(0)
angle_speed = rad(1)

p0_horz = 100
p1_horz = -100
p0 = point_mass(800, 300, 10)
p1 = point_mass(600, 300, 10)
axle = point_mass(700, 300, 10)

fill = True

clock = pygame.time.Clock()

asdf = point_mass(100, 700, 10)
qwer = point_mass(300, 700, 10)

while True:
    display.fill(BLACK) if fill else None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                fill = not fill

    axle.velocity = Velocity(1, rad(90))
    p0.velocity = Velocity(angle_speed * p0_horz, direction=angle+rad(90))
    draw_vector(p0.velocity, p0.x, p0.y, WHITE, display_multiply_factor=20)
    p0.velocity = get_net_vector(p0.velocity, axle.velocity)
    p1.velocity = Velocity(angle_speed * p1_horz, direction=angle+rad(90))
    p1.velocity = get_net_vector(p1.velocity, axle.velocity)

    draw_vector(p0.velocity, p0.x, p0.y, YELLOW, display_multiply_factor=20)
    draw_vector(axle.velocity, axle.x, axle.y, YELLOW, display_multiply_factor=20)

    axle.tick()
    axle.draw()

    p0.tick()
    p0.draw(color=RED)

    p1.tick()
    p1.draw(color=GREEN)

    pygame.draw.line(display, WHITE, (p0.x, D_HEIGHT - p0.y), (p1.x, D_HEIGHT - p1.y))
    angle += rad(1)

    asdf.velocity = Velocity(5, 0)
    draw_vector(asdf.velocity, asdf.x, asdf.y, WHITE, display_multiply_factor=20)
    otherv = Velocity(5, rad(270))
    draw_vector(otherv, asdf.x, asdf.y, WHITE, display_multiply_factor=20)

    asdf.velocity = get_net_vector(asdf.velocity, otherv)
    draw_vector(asdf.velocity, asdf.x, asdf.y, YELLOW, display_multiply_factor=20)

    asdf.tick()
    asdf.draw()

    qwer.velocity = Velocity(5, 0)
    draw_vector(qwer.velocity, qwer.x, qwer.y, WHITE, display_multiply_factor=20)
    qwer.tick()

    otherv = Velocity(5, rad(270))
    draw_vector(otherv, qwer.x, qwer.y, WHITE, display_multiply_factor=20)
    qwer.velocity = otherv
    qwer.tick()


    qwer.draw()

    pygame.display.update()
    clock.tick(60)