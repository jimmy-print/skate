import pygame
import math
from pygame.locals import *

VERT = 'VERT'
HORZ = 'HORZ'

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255


class TwoAxisDirection:
    def __init__(self, sign, XY):
        self.sign = sign
        assert XY == VERT or XY == HORZ
        self.XY = XY


class Force:
    def __init__(self, magnitude, direction, name):
        self.magnitude = magnitude  # newtons
        self.direction = direction
        self.name = name

    def __repr__(self):
        return f'F{self.name} {self.direction.sign} * {self.magnitude} N {self.direct}'


mass = 1
g_accel = 0.05
Fw = Force(g_accel * mass, TwoAxisDirection(sign=-1, XY=VERT), name="weight")

y_forces = []
x_forces = []


def get_net_force(forces):
    # assumes that all forces have same .direction.XY fields
    def ___():
        def __():
            for force in forces:
                yield force.magnitude * force.direction.sign

        for x in __():
            yield x

    return sum(___())


def draw_forces(y_forces__, x_forces__, x, y):
    thik = 2
    for force in y_forces__:
        if force.name == "applied":
            color = RED
        else:
            color = WHITE

        s = font.render(f'F{force.name} {force.magnitude} N', True, WHITE)

        if force.direction.sign == 1:
            height = 100
            pygame.draw.rect(display, color, (x, (D_HEIGHT - y) - height, thik, height))
            display.blit(s, (x + 10, D_HEIGHT - y - height / 2))
        elif force.direction.sign == -1:
            height = 100
            pygame.draw.rect(display, color, (x, D_HEIGHT - y, thik, height))
            display.blit(s, (x + 10, D_HEIGHT - y + height / 2))

    for force in x_forces__:
        if force.name == "applied":
            color = RED
        else:
            color = WHITE

        s = font.render(f'F{force.name} {force.magnitude} N', True, WHITE)

        if force.direction.sign == 1:
            width = 100
            pygame.draw.rect(display, color, (x + width / 10, (D_HEIGHT - y), width, thik))
            display.blit(s, (x + width / 8, D_HEIGHT - y - width / 5))
        elif force.direction.sign == -1:
            width = 100
            pygame.draw.rect(display, color, (x - width, (D_HEIGHT - y), width, thik))
            display.blit(s, (x - s.get_rect().width - width / 8, D_HEIGHT - y - width / 5))


c = {
    "mass": 1,
    "radius": 0,  # moment arm distance?
}

p0 = {
    "mass": 1,
    "radius": 100,
}

p1 = {
    "mass": 1,
    "radius": -100,
}

line = c, p0, p1

# we apply a torque of 1 newton meter consistently (force of 1 newton,
# multiplied by the position vector (radius) = 1.
# theta = 0

# in this case,
# t = r x F
# 1 Nm = 1m x 1 N
# t = moment of inertia * angular acceleration
#     moment of inertia = 1m ** 2 * 1kg
#     moment of inertia = 1kgm^2
# rearrange
# angular acceleration = t / moment of inertia
# angular acceleration = 1 Nm / 1 kgm^2
# ignore N? we certainly do so for regular force calculations
# (linear)
# angular acceleration = 1 rad / s^2
# rad = radius = 1m
# thus tangential acceleration = 1 m / s^

# what about the other two particles?

# at t = 1, angular velocity of p0 = 1 rad / s
# moving counter-clockwise
# p1?
# go again from torque
# t = 1 Nm
# angular acceleration = 1 Nm / moment of inertia
# for p1, moment of inertia = -1m ** 2 * 1 kg
# angular accel = 1 Nm / -1kgm^2

D_WIDTH, D_HEIGHT = 1920, 1080
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.Font("inconsolata.ttf", 15)

BLACK = 0, 0, 0
WHITE = 255, 255, 255

# set individual x and y values for the points dicts
c['x'] = 500
c['y'] = 300

p0['x'] = c['x'] + p0['radius']
p0['y'] = c['y']

p1['x'] = c['x'] + p1['radius']
p1['y'] = c['y']


# LATER MUST FIND CENTER OF MASS OF THESE PARTICLES
# based on given positions and masses
# works currently because symmetrical distribution of mass
# amongst point particles in relation to pre-determined center particle

# though that is not necessary in the case of the skateboard because
# the geometric center of it is the same as the position of the center of mass,
# because skateboard has even mass distribution.


def draw_point(p):
    size = 5
    pygame.draw.rect(display, WHITE, (p['x'], D_HEIGHT - p['y'], size, size))


# want angular acceleration of 0.01 rad / s ^ 2
# 0.01 rad = 0.01 * radius (200px) = 2
# ang. accel. = 2 px / s ^ 2
# ASSUME METERS MEAN PIXELS

# 0.01 rad / s ^ 2
# t = moment inertia * (0.01 rad / s ^ 2)
# moment inertia = 200m ** 2 * 1kg
# moment inertia = 40 000m * 1kg
# t = 40 000kgm * 0.01 rad / s^2
# t = 400Nm??

# torque = 0.1  # newton meters
torque = 0
p0_ang = 0
p0_ang_speed = 0

p1_ang = 0
p1_ang_speed = 0

fpsclock = pygame.time.Clock()
fps_desired = 60

t = 0

y_velocity = 0
x_velocity = 0

while True:
    t += 1
    display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    # t = moment inertia * ang. accel.
    # ang. accel = t / moment inertia
    # ang. accel = 400 Nm / 200m ** 2 ** 1kg
    # ang. accel = 400 Nm / 40 000kgm
    # N / kg = rad / s ^2
    # m / m = 1
    # ang. accel = 0.01 rad / s^2

    if 0 < t < 80:
        y_forces.append(Force(0.1, TwoAxisDirection(sign=1, XY=VERT), name="applied"))
        x_forces.append(Force(0.01, TwoAxisDirection(sign=1, XY=HORZ), name="applied"))

    y_forces.append(Fw)

    draw_forces(y_forces__=y_forces, x_forces__=x_forces, x=p0['x'], y=p0['y'])
    draw_forces(y_forces__=y_forces, x_forces__=x_forces, x=p1['x'], y=p1['y'])
    draw_forces(y_forces__=y_forces, x_forces__=x_forces, x=c['x'], y=c['y'])

    if 0 < t < 2:
        torque = 1
        # TODO draw torque
        # TODO formalise the relationship between torque applied at one point,
        # and the sum of mass of all the particles, and how the resultant acceleration
        # at that point relates to the rest of the particles.
    else:
        torque = 0

    p0_moment_of_inertia = (p0['radius'] ** 2 * p0['mass'])
    # assert p0_moment_of_inertia == 40000
    p0_angaccel = torque / p0_moment_of_inertia
    # assert p0_angaccel == 0.01

    p1_moment_of_inertia = (p1['radius'] ** 2 * p1['mass'])
    p1_angaccel = torque / p1_moment_of_inertia

    p0_ang_speed += p0_angaccel
    p0_ang += p0_ang_speed
    # print(p0_ang)

    p1_ang_speed += p1_angaccel
    p1_ang += p1_ang_speed

    '''
    c['x'] = center_x
    c['y'] = center_y  # TODO simplify this
    '''

    p0_dx = math.cos(p0_ang * 180 / math.pi) * p0['radius']
    p0['x'] = c['x'] + p0_dx

    p0_dy = math.sin(p0_ang * 180 / math.pi) * p0['radius']
    p0['y'] = c['y'] + p0_dy

    p1_dx = math.cos(p0_ang * 180 / math.pi) * p0['radius']
    p1['x'] = c['x'] - p0_dx

    p1_dy = math.sin(p1_ang * 180 / math.pi) * p1['radius']
    p1['y'] = c['y'] + p1_dy

    print(p0_angaccel, p0_ang_speed)

    y_accel = get_net_force(y_forces) / mass
    y_velocity += y_accel
    p0['y'] += y_velocity
    p1['y'] += y_velocity
    c['y'] += y_velocity

    x_accel = get_net_force(x_forces) / mass
    x_velocity += x_accel
    p0['x'] += x_velocity
    p1['x'] += x_velocity
    c['x'] += x_velocity

    draw_point(c)
    draw_point(p0)
    draw_point(p1)

    pygame.draw.line(display, WHITE, (p0['x'], D_HEIGHT - p0['y']), (p1['x'], D_HEIGHT - p1['y']))

    y_forces = []
    x_forces = []

    pygame.display.update()
    fpsclock.tick(fps_desired)
