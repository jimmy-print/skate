import random
import pygame
from math import sin, cos, sqrt, acos
from utils import *

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
ORANGE = 255, 165, 0
PINK = 255, 0, 0

INFINITY = 10000000000000

g_accel = 0.3

D_WIDTH, D_HEIGHT = 1280, 720
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.SysFont("Ubuntu", 15)


class Vector:  # as in physics, not c++ type of vector
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude  # whatever is appropriate. for example, for Force,
        # the magnitude field is newtons.
        self.direction = direction  # radians relative to x-axis

    def __repr__(self):
        raise NotImplementedError

class Velocity(Vector):
    def __init__(self, speed, direction):
        super().__init__(speed, direction)

    @property
    def speed(self):
        return self.magnitude

    def __repr__(self):
        return f'velocity {round(self.magnitude)}pxs/frm {round(deg(self.direction))}°'

class Force(Vector):
    def __init__(self, newtons, direction, name='placeholder_force_name'):
        super().__init__(newtons, direction)
        self.name = name

    def __repr__(self):
        return f'F{self.name} {round(self.magnitude)}N {round(deg(self.direction))}°'


def get_x_y_components(vector):
    return (
        cos(vector.direction) * vector.magnitude,
        sin(vector.direction) * vector.magnitude
    )


def recombine(x_mag, y_mag, type_):
    hypo = sqrt(x_mag ** 2 + y_mag ** 2)
    return type_(hypo, direction=acos(x_mag / hypo))


def get_net_vector(v0, v1):
    # using triangle rule for vector addition
    # todo explain method, with co-interior angles and cosine rule

    assert type(v0) == type(v1)
    # todo assert parent class is Vector
    vector_type = type(v0)

    if norm(v0.direction) <= norm(v1.direction):
        v00 = v0
        v11 = v1
    elif norm(v0.direction) > norm(v1.direction):
        v00 = v1
        v11 = v0

    if v00.magnitude < 0 or v11.magnitude < 0:
        class ShitException(Exception): pass
        raise ShitException('negative magnitudes not accepted, fix yo shit')

    a = v00.magnitude
    b = v11.magnitude
    gamma = rad(360) - (norm(v11.direction) + (rad(180) - norm(v00.direction)))

    c = math.sqrt(a**2 + b**2 - 2*a*b*math.cos(gamma))

    if v00.magnitude == 0:
        return v11
    elif v11.magnitude == 0:
        return v00

    if c == 0:
        net_force = vector_type(c, 0)
    else:
        thing_to_acos = (c**2 + a**2 - b**2) / (2 * a * c) # TODO give better names for these variables
        if thing_to_acos > 1:
            # assume that it is something like 1.000002 as caused by floating point error
            thing_to_acos = 1
        if thing_to_acos < -1:
            thing_to_acos = -1
        new_direction = math.acos( thing_to_acos )
        if gamma < 0:
            new_direction = rad(360) - new_direction

        net_force = vector_type(c, norm(norm(v00.direction) + norm(new_direction)))

    return net_force


def get_net_force(fs):
    tmp_f = fs[0]
    for f in fs[1:len(fs)]:
        tmp_f = get_net_vector(tmp_f, f)
    tmp_f.name = 'net'
    return tmp_f


def draw_vector(vector, x, y, color, display_multiply_factor=100):
    draw_mag = vector.magnitude * display_multiply_factor

    pygame.draw.line(display, color,
                     (x, D_HEIGHT - y),
                     (x + math.cos(vector.direction) * draw_mag, D_HEIGHT - (y + math.sin(vector.direction) * draw_mag)))

    endpos = [x + math.cos(vector.direction) * draw_mag, D_HEIGHT - (y + math.sin(vector.direction) * draw_mag)]
    endpos[0] = round(endpos[0])
    endpos[1] = round(endpos[1])

    draw_text(repr(vector), *endpos)


class point_mass:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y

        self.mass = mass

        self.will_apply_forces = []
        self.velocity = Velocity(0, 0)

    def add_force(self, force):
        self.will_apply_forces.append(force)

    def apply_forces(self):
        net = get_net_force(self.will_apply_forces)

        dv = Velocity(net.magnitude / self.mass, net.direction)

        self.velocity = get_net_vector(dv, self.velocity)


    def tick(self):
        self.x += math.cos(self.velocity.direction) * self.velocity.speed
        self.y += math.sin(self.velocity.direction) * self.velocity.speed

    def draw(self, color=WHITE):
        point_draw_width = 5
        point_draw_height = 5
        display.fill(color, ((self.x, D_HEIGHT - self.y), (point_draw_width, point_draw_height)))

        '''
        if len(self.will_apply_forces) > 0:
            for force in self.will_apply_forces:
                draw_vector(force, self.x, self.y, color=WHITE)
            draw_vector(get_net_force(self.will_apply_forces), x=self.x, y=self.y, color=GREEN)
        '''

    @staticmethod
    def collide(p0, p1):
        p0_x_velocity, p0_y_velocity = get_x_y_components(p0.velocity)
        p1_x_velocity, p1_y_velocity = get_x_y_components(p1.velocity)

        # COLLIDE!
        φ = 0  # collision angle
        # since these are point masses, just use 0
        p0_new_x_velocity = ((p0.velocity.speed * cos(p0.velocity.direction - φ) * (
                p0.mass - p1.mass) + 2 * p1.mass * p1.velocity.speed * cos(p1.velocity.direction - φ)) / (
                                     p0.mass + p1.mass)) * cos(φ) + p0.velocity.speed * sin(
            p0.velocity.direction - φ) * cos(φ + math.pi / 2)
        p0_new_y_velocity = ((p0.velocity.speed * cos(p0.velocity.direction - φ) * (
                p0.mass - p1.mass) + 2 * p1.mass * p1.velocity.speed * cos(p1.velocity.direction - φ)) / (
                                     p0.mass + p1.mass)) * sin(φ) + p0.velocity.speed * sin(
            p0.velocity.direction - φ) * sin(φ + math.pi / 2)

        p1_new_x_velocity = ((p1.velocity.speed * cos(p1.velocity.direction - φ) * (
                p1.mass - p0.mass) + 2 * p0.mass * p0.velocity.speed * cos(p0.velocity.direction - φ)) / (
                                     p1.mass + p0.mass)) * cos(φ) + p1.velocity.speed * sin(
            p1.velocity.direction - φ) * cos(φ + math.pi / 2)
        p1_new_y_velocity = ((p1.velocity.speed * cos(p1.velocity.direction - φ) * (
                p1.mass - p0.mass) + 2 * p0.mass * p0.velocity.speed * cos(p0.velocity.direction - φ)) / (
                                     p1.mass + p0.mass)) * sin(φ) + p1.velocity.speed * sin(
            p1.velocity.direction - φ) * sin(φ + math.pi / 2)

        p0.velocity = recombine(p0_new_x_velocity, p0_new_y_velocity, type_=Velocity)
        p1.velocity = recombine(p1_new_x_velocity, p1_new_y_velocity, type_=Velocity)

class axle__(point_mass):
    pass

class point_mass_on_line(point_mass):
    def __init__(self, axle, orig_horz_d_from_axle, mass):
        self.orig_horz_d_from_axle = orig_horz_d_from_axle  # moment arm as well for now since force is only applied
        # tangentially

        super().__init__(axle.x + self.orig_horz_d_from_axle, axle.y, mass)
        self.rotational_inertia = self.mass * self.orig_horz_d_from_axle ** 2
        # aka moment of inertia


class line:
    def __init__(self, axle, points):  # TODO clean up data entry
        self.axle = axle
        self.points = points

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

    # TODO allow applying multiple forces at different radial distances in one frm.
    # thus split apply_force to add_force and apply_force,
    # like how point_mass does it.
    def apply_force(self, force: Force, distance_from_axle_on_line: int):
        # if distance_from_axle_on_line is positive number that means towards the right, negative means left

        # at high speeds this doesn't sync with the line because it is one frm behind or something like that.
        draw_vector(force, self.axle.x + cos(self.angle) * distance_from_axle_on_line, self.axle.y + sin(self.angle) * distance_from_axle_on_line, color=WHITE, display_multiply_factor=20)

        if distance_from_axle_on_line == 0:
            dv = Velocity(force.magnitude / self.mass, force.direction)
            self.axle.velocity = get_net_vector(self.axle.velocity, dv)
        else:
            torque = force.magnitude * distance_from_axle_on_line * sin(force.direction - self.angle)

            self.angular_acceleration = torque / self.rotational_inertia
            self.angular_speed += self.angular_acceleration

    def tick(self):
        self.angle += self.angular_speed  # should still be in radians at this point

        if deg(self.angle) > 360:
            self.angle = rad(deg(self.angle) - 360)

        self.axle.tick()

        # now, from self.angular_speed and self.angle, derive tangential velocity vectors for every point besides the axle.
        for point in self.points:
            if point.orig_horz_d_from_axle > 0:
                if self.angular_speed > 0:
                    point.velocity = Velocity(point.orig_horz_d_from_axle * self.angular_speed, self.angle + rad(90))
                elif self.angular_speed < 0:
                    point.velocity = Velocity(abs(point.orig_horz_d_from_axle) * abs(self.angular_speed), self.angle + rad(270))
                else:
                    point.velocity = Velocity(0, 0)
            elif point.orig_horz_d_from_axle < 0:
                if self.angular_speed > 0:
                    point.velocity = Velocity(abs(point.orig_horz_d_from_axle) * self.angular_speed, self.angle + rad(270))
                elif self.angular_speed < 0:
                    point.velocity = Velocity(abs(point.orig_horz_d_from_axle) * abs(self.angular_speed),
                                              self.angle + rad(90))
                else:
                    point.velocity = Velocity(0, 0)
            point.rot_velocity = point.velocity

            # all this shit is because negative magnitude values fuck up the net vector function.

            draw_vector(point.velocity, point.x, point.y, color=GREEN, display_multiply_factor=20)
            draw_vector(self.axle.velocity, point.x, point.y, color=YELLOW, display_multiply_factor=20)

            v = get_net_vector(point.velocity, self.axle.velocity)
            draw_vector(v, point.x, point.y, RED, display_multiply_factor=20)
            point.velocity = v
            point.tick()

    def draw(self):
        # draw entire line
        pygame.draw.line(display, WHITE, (self.leftmostpoint.x, D_HEIGHT - self.leftmostpoint.y),
                         (self.rightmostpoint.x, D_HEIGHT - self.rightmostpoint.y))

        # draw axle
        axle_width = 10
        axle_height = 10
        display.fill(WHITE, ((self.axle.x, D_HEIGHT - self.axle.y), (axle_width, axle_height)))

        # draw individual points
        point_draw_width = 5
        point_draw_height = 5

        for point in self.points:
            display.fill(RED, ((point.x, D_HEIGHT - point.y), (point_draw_width, point_draw_height)))

        draw_text(f'+', self.rightmostpoint.x, D_HEIGHT - self.rightmostpoint.y)
        draw_text(f'-', self.leftmostpoint.x, D_HEIGHT - self.leftmostpoint.y)

    def reset_handovers(self):
        self.handover_force = None
        self.handover_radial_distance = None


def main():
    init_axle_x = 300
    init_axle_y = 200
    axle = axle__(init_axle_x, init_axle_y, 10)
    l = line(axle, (
        point_mass_on_line(axle, 250, 20),
        point_mass_on_line(axle, -250, 20)
    ))

    t = 0
    fill = True

    fpsclock = pygame.time.Clock()
    fps_desired = 60

    def pause():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
                if event.type == pygame.QUIT:
                    quit()

    p0 = point_mass(0, 200, 1)
    p0.velocity = Velocity(1.41, -rad(26.3))
    p1 = point_mass(200, 100, 1)

    frm_by_frm = False

    def snow_crash(point, hiro_protagonist):
        pxv, pyv = get_x_y_components(point.velocity)

        if hiro_protagonist == 'x':
            pxv = pxv
            pyv = -pyv
        elif hiro_protagonist == 'y':
            pxv = -pxv
            pyv = pyv

        point.velocity = recombine(pxv, pyv, Velocity)
        draw_vector(point.velocity, point.x, point.y, GREEN, display_multiply_factor=20)
    done = False
    l.axle.velocity = Velocity(10
                               , rad(0))
    while True:
        t += 1
        pausing_this_frm = False

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
                    pausing_this_frm = True
                if event.key == pygame.K_f:
                    frm_by_frm = not frm_by_frm

        pygame.draw.line(display, WHITE, (0, D_HEIGHT - 100), (D_WIDTH, D_HEIGHT - 100))
        pygame.draw.polygon(display, WHITE, ((l.axle.x, D_HEIGHT - l.axle.y), (l.axle.x - 50, D_HEIGHT - (l.axle.y - 100)), (l.axle.x + 50, D_HEIGHT - (l.axle.y - 100))), width=2)

        l.angular_acceleration = 0

        if 0 < t < 18:
            l.apply_force(Force(100, rad(270)), distance_from_axle_on_line=-100)
        if 20 < t < 30:
            l.apply_force(Force(20, rad(deg(l.angle) - 90)), distance_from_axle_on_line=200)

        if l.leftmostpoint.y < 100 and t < 60:
            l.angular_speed = 0
            #l.apply_force(get_net_vector(Force(l.leftmostpoint.rot_velocity.speed * l.mass, l.leftmostpoint.rot_velocity.direction + rad(180)),
            #                            Force(l.axle.velocity.speed * l.mass, rad(0))), 0)
            l.axle.velocity = get_net_vector(Velocity(l.leftmostpoint.rot_velocity.speed, l.leftmostpoint.rot_velocity.direction + rad(180)),
                                             Velocity(l.axle.velocity.speed, l.axle.velocity.direction))

        # forces can be stacked on the line if they're applied at the axle, not otherwise for torque
        # kinda sure??
        if 30 < t < 40:
            l.apply_force(Force(20, l.angle + rad(270)), distance_from_axle_on_line=0)
        if l.axle.y > 200:
            l.apply_force(Force(g_accel * l.mass, rad(270)), 0)


        l.tick()
        l.draw()

        l.reset_handovers()

        if abs(round(p0.x) - round(p1.x)) < 3 and abs(round(p0.y) - round(p1.y)) < 3:
            point_mass.collide(p0, p1)
        p0.tick(); p0.draw(WHITE)
        p1.tick(); p1.draw(RED)

        pygame.display.update()
        fpsclock.tick(fps_desired)

        if pausing_this_frm:
            draw_text('Paused', 200, 80)
            pygame.display.update()
            pause()

        if frm_by_frm:
            if input() == 'f':
                frm_by_frm = not frm_by_frm


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


if __name__ == '__main__':
    main()
