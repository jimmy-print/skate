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

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class line:
    def __init__(self):
        self.axle = point(400, 400)
        self.radius = 500

        self.right_point = point(self.axle.x + self.radius, self.axle.y)
        self.center_point = point(self.axle.x, self.axle.y)
        self.left_point = point(self.axle.x - self.radius, self.axle.y)

        self.right_point_mass = 5
        self.center_point_mass = 5
        self.left_point_mass = 5

        self.angle = 0  # in degrees, measuring how far the rightmost point (at the start) is from the x-axis
        # actually it's all the same, both for the rightmost point and the middle point between the center
        # and the rightmost point, because of how angles work
        self.angular_speed = 0

        self.rotation_inertia = ( (self.right_point_mass * self.radius ** 2)
                                + (self.left_point_mass * (-self.radius) ** 2)
                                + (self.center_point_mass * 0 ** 2) )
        # perfectly logical that the center point contributes nothing to the rotational inertia,
        # because it doesn't rotate at all since it's the same as the axle

    def apply_force(self, force):
        # radial length meaning length along the radius, not sure what the proper term is.
        # if radial_length is positive number that means towards the right, negative means left
        torque = force * self.radius

        angular_acceleration = torque / self.rotation_inertia
        self.angular_speed += angular_acceleration
        self.angle += self.angular_speed  # should still be in radians at this point

        rightpointdx = math.cos(self.angle * 180 / math.pi) * self.radius
        rightpointdy = math.sin(self.angle * 180 / math.pi) * self.radius  # TODO make deg/rad functions

        leftpointdx = math.cos(self.angle * 180 / math.pi) * self.radius  # something not quite right
        # about the signs here. it's probably not accurate to call it dx when you have to subtract it
        leftpointdy = math.sin(self.angle * 180 / math.pi) * self.radius

        self.right_point.x = self.axle.x + rightpointdx
        self.right_point.y = self.axle.y + rightpointdy

        self.left_point.x = self.axle.x - leftpointdx
        self.left_point.y = self.axle.y - leftpointdy


    def draw(self):
        axle_width = 10
        axle_height = 10
        display.fill(WHITE, ((self.axle.x, D_HEIGHT - self.axle.y), (axle_width, axle_height)))

        pygame.draw.line(display, WHITE, (self.left_point.x, D_HEIGHT - self.left_point.y),
                         (self.right_point.x, D_HEIGHT - self.right_point.y))


l = line()

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

fill = True

while True:
    t += 1
    if fill:
        display.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                fill = not fill

    # t = moment inertia * ang. accel.
    # ang. accel = t / moment inertia
    # ang. accel = 400 Nm / 200m ** 2 ** 1kg
    # ang. accel = 400 Nm / 40 000kgm
    # N / kg = rad / s ^2
    # m / m = 1
    # ang. accel = 0.01 rad / s^2

    if 0 < t < 80:
        y_forces.append(Force(0.1, TwoAxisDirection(sign=1, XY=VERT), name="applied"))
        x_forces.append(Force(0.03, TwoAxisDirection(sign=1, XY=HORZ), name="applied"))

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

        # GOT the part above
        # just treat the whole line as one center of mass
        # but take into account the geometric position where the torque is applied
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

    p0_dx = math.cos(p0_ang * 180 / math.pi) * p0['radius']
    p0['x'] = c['x'] + p0_dx

    p0_dy = math.sin(p0_ang * 180 / math.pi) * p0['radius']
    p0['y'] = c['y'] + p0_dy

    p1_dx = math.cos(p1_ang * 180 / math.pi) * p1['radius']
    p1['x'] = c['x'] - p0_dx

    p1_dy = math.sin(p1_ang * 180 / math.pi) * p1['radius']
    p1['y'] = c['y'] + p1_dy

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

    l.apply_force(0.01)
    l.draw()

    y_forces = []
    x_forces = []

    display.blit(font.render(f'press q to toggle parabolic ecstasy', True, WHITE), (10, 200))

    pygame.display.update()
    fpsclock.tick(fps_desired)
