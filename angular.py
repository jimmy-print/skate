import pygame
import math
from utils import *

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

g_accel = 0.05

D_WIDTH, D_HEIGHT = 1600, 900
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.SysFont("Ubuntu", 15)

fpsclock = pygame.time.Clock()
fps_desired = 60


class Force:
    def __init__(self, magnitude, direction, name='placeholder_name'):
        self.magnitude = magnitude  # newtons
        self.direction = direction  # radians relative to x-axis
        self.name = name

    def __repr__(self):
        if self.direction is not None:
            return f'F{self.name} {self.magnitude}newtons {deg(self.direction)}°'
        else:
            return f'F{self.name} {self.magnitude}newtons non-existent-force°'


def get_net_force_two_forces(f0, f1):
    # using triangle rule for vector addition
    # todo explain method, with co-interior angles and cosine rule

    if norm(f0.direction) <= norm(f1.direction):
        f00 = f0
        f11 = f1
    elif norm(f0.direction) > norm(f1.direction):
        f00 = f1
        f11 = f0

    a = f00.magnitude
    b = f11.magnitude
    gamma = rad(360) - (norm(f11.direction) + (rad(180) - norm(f00.direction)))

    c = math.sqrt(a**2 + b**2 - 2*a*b*math.cos(gamma))

    if c == 0:
        net_force = Force(c, None, 'a')  # when direction is None, it means that the force is non-existent.
        # the object still remains, however, because it makes finding the net force by looping over a list of
        # forces easier. todo explain why
    else:
        thing_to_acos = (c**2 + a**2 - b**2) / (2 * a * c) # TODO give better names for these variables
        if thing_to_acos > 1:
            # assume that it is something like 1.000002 as caused by floating point error
            thing_to_acos = 1
        new_direction = math.acos( thing_to_acos )
        if gamma < 0:
            new_direction = rad(360) - new_direction

        net_force = Force(c, norm(norm(f00.direction) + norm(new_direction)), 'a')

    return net_force


def get_net_force(fs):
    tmp_f = fs[0]
    for f in fs[1:len(fs)]:
        if tmp_f.direction is not None:
            tmp_f = get_net_force_two_forces(tmp_f, f)
        else:
            tmp_f = f
    return tmp_f


def draw_forces(forces__, x, y, colors):
    for force in forces__:
        s = font.render(f'F{force.name} {force.magnitude} N', True, WHITE)

        draw_mag = force.magnitude * 100

        pygame.draw.line(display, colors,
                         (x, D_HEIGHT - y),
                         (x + math.cos(force.direction) * draw_mag, D_HEIGHT - (y + math.sin(force.direction) * draw_mag)))


class point_mass_on_line:
    def __init__(self, orig_horz_d_from_axle, mass):
        self.orig_horz_d_from_axle = orig_horz_d_from_axle  # moment arm as well for now since force is only applied
        # tangentially

        self.x = None
        self.y = None

        self.mass = mass
        self.rotational_inertia = self.mass * self.orig_horz_d_from_axle ** 2


class line:
    def __init__(self, axle, points):  # TODO clean up data entry
        self.axle = axle
        self.points = points

        # set abs x and y values for the points
        for point in points:
            point.x = self.axle[0] + point.orig_horz_d_from_axle
            point.y = self.axle[1]

        assert all_same([point.y for point in self.points])
        assert all_unique([point.x for point in self.points])

        smallest = self.points[0]
        for point__ in self.points:
            if point__.x < smallest.x:
                smallest = point__
        self.leftmostpoint = smallest
        largest = self.points[0]
        for point__ in self.points:
            if point__.x > largest.x:
                largest = point__
        self.rightmostpoint = largest

        self.angle = 0
        self.angular_acceleration = 0
        self.angular_speed = 0

        self.rotational_inertia = sum(point.rotational_inertia for point in self.points)

        self.mass = sum(point.mass for point in self.points)

        self.handover_radial_distance = None  # todo explain what handover* is
        self.handover_force = None

    def apply_force(self, force, radial_distance):
        # radial distance meaning length along the radius, not sure what the proper term is.
        # DOES NOT MEAN 'RELATING TO RADIAN'
        # if radial_distance is positive number that means towards the right, negative means left

        assert radial_distance != 0

        self.handover_radial_distance = radial_distance
        self.handover_force = force

        torque = force * radial_distance

        self.angular_acceleration = torque / self.rotational_inertia
        self.angular_speed += self.angular_acceleration

    def tick(self):
        self.angle += self.angular_speed  # should still be in radians at this point

        if deg(self.angle) > 360:
            self.angle = rad(deg(self.angle) - 360)

        for point in self.points:
            pointdx = math.cos(self.angle) * point.orig_horz_d_from_axle
            pointdy = math.sin(self.angle) * point.orig_horz_d_from_axle

            point.x = self.axle[0] + pointdx
            point.y = self.axle[1] + pointdy

    def draw(self):
        # draw entire line
        pygame.draw.line(display, WHITE, (self.leftmostpoint.x, D_HEIGHT - self.leftmostpoint.y),
                         (self.rightmostpoint.x, D_HEIGHT - self.rightmostpoint.y))

        # draw axle
        axle_width = 10
        axle_height = 10
        display.fill(WHITE, ((self.axle[0], D_HEIGHT - self.axle[1]), (axle_width, axle_height)))

        # draw individual points
        point_draw_width = 5
        point_draw_height = 5

        for point in self.points:
            display.fill(RED, ((point.x, D_HEIGHT - point.y), (point_draw_width, point_draw_height)))

        draw_text(f'+', self.rightmostpoint.x, D_HEIGHT - self.rightmostpoint.y)
        draw_text(f'-', self.leftmostpoint.x, D_HEIGHT - self.leftmostpoint.y)


        # overlay torque 'freebody' diagram
        if self.handover_force is not None and self.handover_radial_distance is not None:
            ellipse_bounding_rect = (
                self.axle[0] - abs(self.handover_radial_distance),
                D_HEIGHT - self.axle[1] - abs(self.handover_radial_distance),
                abs(self.handover_radial_distance * 2),
                abs(self.handover_radial_distance * 2)
            )

            if self.handover_radial_distance > 0:
                stop = self.angle
                start = stop - rad(self.handover_force)

            elif self.handover_radial_distance < 0:
                start = self.angle + rad(180)
                stop = start + rad(self.handover_force)

            if self.handover_force < 0:
                start, stop = stop, start

            # a bit behind the actual line because it takes the previous frame angle
            pygame.draw.arc(display, GREEN, ellipse_bounding_rect, start_angle=start, stop_angle=stop)

    def reset_handovers(self):
        self.handover_force = None
        self.handover_radial_distance = None


def main():
    axle = [200, 200]
    l = line(axle, (
        point_mass_on_line(200, 10),
        point_mass_on_line(-200, 10)
    ))

    t = 0
    fill = True

    forces = []

    def pause():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
                if event.type == pygame.QUIT:
                    quit()

    dx = 0
    dy = 0

    while True:
        t += 1
        if fill:
            display.fill(BLACK)
        draw_text(f't={t}', 100, 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    fill = not fill
                if event.key == pygame.K_SPACE:
                    pause()

        forces.append(Force(g_accel * l.mass, rad(270), name="weight"))
        if 0 < t < 90:
            forces.append(Force(0.5, rad(0), name="applied"))

            forces.append(Force(2, rad(90), name="applied"))

        net_force = get_net_force(forces)
        accel = net_force.magnitude / l.mass

        ddx = math.cos(net_force.direction) * accel
        ddy = math.sin(net_force.direction) * accel

        dx += ddx
        dy += ddy

        l.axle[0] += dx
        l.axle[1] += dy

        draw_forces(forces__=forces, y=l.axle[1], x=l.axle[0], colors=WHITE)
        draw_forces(forces__=(net_force,), y=l.axle[1], x=l.axle[0], colors=GREEN)

        l.angular_acceleration = 0

        if 0 < t < 20:
            l.apply_force(-5, -200)

        l.tick()
        l.draw()

        l.reset_handovers()

        forces = []

        draw_text(f'θ={round(deg(l.angle))}', 100, 100)

        pygame.display.update()
        fpsclock.tick(fps_desired)


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


if __name__ == '__main__':
    main()
