import pygame
import time
import math
from pygame.locals import *

c = {
    "mass": 1,
    "radius": 0,  # moment arm distance?
}

p0 = {
    "mass": 1,
    "radius": 300,
}

p1 = {
    "mass": 1,
    "radius": -300,
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
# angular accel = 1 Nm / -1kgm^2 BUT WHAT ABOUT THE NEGATIVE?? if ignore it makes sense

# OHHHH angular accel is the same anyways for the particle on the other side
# because it is stil turning counter-clockwise like p0


D_WIDTH, D_HEIGHT = 1280, 720
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

BLACK = 0, 0, 0
WHITE = 255, 255, 255


center_x, center_y = 500, 300

# set individual x and y values for the points dicts
c['x'] = center_x
c['y'] = center_y

p0['x'] = center_x + p0['radius']
p0['y'] = center_y

p1['x'] = center_x + p1['radius']
p1['y'] = center_y


# LATER MUST FIND CENTER OF MASS OF THESE PARTICLES
# based on given positions and masses
# works currently because symmetrical distribution of mass
# amongst point particles in relation to pre-determined center particle


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

torque = 0.1  # newton meters
p0_ang = 0
p0_ang_speed = 0

p1_ang = 0
p1_ang_speed = 0

fpsclock = pygame.time.Clock()
fps_desired = 60
    
while True:
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
    p0_moment_of_inertia = (p0['radius'] ** 2 * p0['mass'])
    #assert p0_moment_of_inertia == 40000
    p0_angaccel = torque / p0_moment_of_inertia
    #assert p0_angaccel == 0.01

    p1_moment_of_inertia = (p1['radius'] ** 2 * p1['mass'])
    p1_angaccel = torque / p1_moment_of_inertia

    p0_ang_speed += p0_angaccel
    p0_ang += p0_ang_speed
    #print(p0_ang)

    p1_ang_speed += p1_angaccel
    p1_ang += p1_ang_speed

    p0_dx = math.cos(p0_ang * 180 / math.pi) * p0['radius']
    p0['x'] = center_x + p0_dx

    p0_dy = math.sin(p0_ang * 180 / math.pi) * p0['radius']
    p0['y'] = center_y + p0_dy

    p1_dx = math.cos(p0_ang * 180 / math.pi) * p0['radius']
    p1['x'] = center_x - p0_dx

    p1_dy = math.sin(p1_ang * 180 / math.pi) * p1['radius']
    p1['y'] = center_y + p1_dy



    
    
    draw_point(c)
    draw_point(p0)
    draw_point(p1)

    pygame.draw.line(display, WHITE, (p0['x'], D_HEIGHT - p0['y']), (p1['x'], D_HEIGHT - p1['y']))

    pygame.display.update()
    fpsclock.tick(fps_desired)
