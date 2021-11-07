import math
from math import sin, cos, sqrt, acos
from utils import rad, deg
from angular import point_mass, Velocity, display, pygame, BLACK, GREEN, WHITE

p0 = point_mass(x=10, y=10, mass=10)
p1 = point_mass(x=500, y=10, mass=1)

# TODO have rad and deg classes so they're never mixed up

p0.velocity = Velocity(speed=1, direction=rad(10))
p1.velocity = Velocity(speed=1, direction=rad(170))


def get_x_y_components(vector):
    return (
        cos(vector.direction) * vector.magnitude,
        sin(vector.direction) * vector.magnitude
    )


def recombine(x_mag, y_mag, type_):
    hypo = sqrt(x_mag ** 2 + y_mag ** 2)
    return type_(hypo, direction=acos(x_mag / hypo))


while True:
    display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    p0.tick()
    p1.tick()

    if round(p0.x) == round(p1.x) and round(p0.y) == round(p1.y):
        p0.x_velocity, p0.y_velocity = get_x_y_components(p0.velocity)
        p1.x_velocity, p1.y_velocity = get_x_y_components(p1.velocity)

        # COLLIDE!
        φ = 0  # collision angle
        # since these are point masses, just use 0
        p0.new_x_velocity = ((p0.velocity.speed * cos(p0.velocity.direction - φ) * (
                p0.mass - p1.mass) + 2 * p1.mass * p1.velocity.speed * cos(p1.velocity.direction - φ)) / (
                                     p0.mass + p1.mass)) * cos(φ) + p0.velocity.speed * sin(
            p0.velocity.direction - φ) * cos(φ + math.pi / 2)
        p0.new_y_velocity = ((p0.velocity.speed * cos(p0.velocity.direction - φ) * (
                p0.mass - p1.mass) + 2 * p1.mass * p1.velocity.speed * cos(p1.velocity.direction - φ)) / (
                                     p0.mass + p1.mass)) * sin(φ) + p0.velocity.speed * sin(
            p0.velocity.direction - φ) * sin(φ + math.pi / 2)

        p1.new_x_velocity = ((p1.velocity.speed * cos(p1.velocity.direction - φ) * (
                p1.mass - p0.mass) + 2 * p0.mass * p0.velocity.speed * cos(p0.velocity.direction - φ)) / (
                                     p1.mass + p0.mass)) * cos(φ) + p1.velocity.speed * sin(
            p1.velocity.direction - φ) * cos(φ + math.pi / 2)
        p1.new_y_velocity = ((p1.velocity.speed * cos(p1.velocity.direction - φ) * (
                p1.mass - p0.mass) + 2 * p0.mass * p0.velocity.speed * cos(p0.velocity.direction - φ)) / (
                                     p1.mass + p0.mass)) * sin(φ) + p1.velocity.speed * sin(
            p1.velocity.direction - φ) * sin(φ + math.pi / 2)

        p0.velocity = recombine(p0.new_x_velocity, p0.new_y_velocity, Velocity)
        p1.velocity = recombine(p1.new_x_velocity, p1.new_y_velocity, Velocity)

    p0.draw(GREEN)

    p1.draw(WHITE)

    pygame.display.update()
