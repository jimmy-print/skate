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
GREY = 50, 50, 50

INFINITY = 10000000000000

g_accel = 0.7

D_WIDTH, D_HEIGHT = 4000, 800
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.SysFont("Ubuntu", 15)

debug = True


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
        #return f'velocity {round(self.magnitude)}pxs/frm {round(deg(self.direction))}°'
        return f'velocity {(self.magnitude)}pxs/frm {(round(deg(self.direction)))}°'


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

1
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
    if not debug:
        return
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
        self.horz = orig_horz_d_from_axle  # moment arm as well for now since force is only applied
        # tangentially

        super().__init__(axle.x + self.horz, axle.y, mass)
        self.rotational_inertia = self.mass * self.horz ** 2
        # aka moment of inertia


class line:
    LEFT = 'LEFT'
    CENT = 'CENT'
    RIGH = 'RIGH'
    def __init__(self, axle, points, wheels_horz_d, length):  # TODO clean up data entry
        self.length = length
        self.axle = axle
        self.points = points
        self.wheels_horz_d = wheels_horz_d

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

        self.axle_loc = line.LEFT

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
            if point.horz > 0:
                if self.angular_speed > 0:
                    point.velocity = Velocity(point.horz * self.angular_speed, self.angle + rad(90))
                elif self.angular_speed < 0:
                    point.velocity = Velocity(abs(point.horz) * abs(self.angular_speed), self.angle + rad(270))
                else:
                    point.velocity = Velocity(0, 0)
            elif point.horz < 0:
                if self.angular_speed > 0:
                    point.velocity = Velocity(abs(point.horz) * self.angular_speed, self.angle + rad(270))
                elif self.angular_speed < 0:
                    point.velocity = Velocity(abs(point.horz) * abs(self.angular_speed),
                                              self.angle + rad(90))
                else:
                    point.velocity = Velocity(0, 0)
            point.rot_velocity = point.velocity
            # ^^^
            # all this shit is because negative magnitude values fuck up the net vector function.

            draw_vector(point.velocity, point.x, point.y, color=GREEN, display_multiply_factor=10) if point.velocity.magnitude != 0 else None
            draw_vector(self.axle.velocity, point.x, point.y, color=YELLOW, display_multiply_factor=10) if self.axle.velocity.magnitude != 0 else None

            v = get_net_vector(point.velocity, self.axle.velocity)
            if self.axle.velocity.magnitude != 0:
                draw_vector(v, point.x, point.y, RED, display_multiply_factor=10)
            point.velocity = v
            point.tick()
        draw_vector(self.axle.velocity, self.axle.x, self.axle.y, color=YELLOW, display_multiply_factor=10) if self.axle.velocity.magnitude != 0 else None

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

    def maintain_axle(self, axle_loc):
        if axle_loc == self.axle_loc:
            return

        self.axle_loc = axle_loc

        if axle_loc == line.CENT:
            self.axle.x = self.leftmostpoint.x + cos(self.angle) * self.length / 2
            self.axle.y = self.leftmostpoint.y + sin(self.angle) * self.length / 2

            self.leftmostpoint = point_mass_on_line(self.axle, -1 * self.length / 2, self.leftmostpoint.mass)
            self.rightmostpoint = point_mass_on_line(self.axle, self.length / 2, self.rightmostpoint.mass)
        elif axle_loc == line.LEFT:
            self.axle.x = self.leftmostpoint.x + cos(self.angle) * self.wheels_horz_d
            self.axle.y = self.leftmostpoint.y + sin(self.angle) * self.wheels_horz_d

            self.leftmostpoint = point_mass_on_line(self.axle, -1 * self.wheels_horz_d, self.leftmostpoint.mass)
            self.rightmostpoint = point_mass_on_line(self.axle, (self.length - self.wheels_horz_d), self.rightmostpoint.mass)
        elif axle_loc == line.RIGH:
            self.axle.x = self.leftmostpoint.x + cos(self.angle) * (self.length - self.wheels_horz_d)
            self.axle.y = self.leftmostpoint.y + sin(self.angle) * (self.length - self.wheels_horz_d)

            self.leftmostpoint = point_mass_on_line(self.axle, -(self.length - self.wheels_horz_d), self.leftmostpoint.mass)
            self.rightmostpoint = point_mass_on_line(self.axle, self.wheels_horz_d, self.rightmostpoint.mass)

        self.leftmostpoint.x = self.axle.x + math.cos(self.angle) * self.leftmostpoint.horz
        self.leftmostpoint.y = self.axle.y + math.sin(self.angle) * self.leftmostpoint.horz

        self.rightmostpoint.x = self.axle.x + math.cos(self.angle) * self.rightmostpoint.horz
        self.rightmostpoint.y = self.axle.y + math.sin(self.angle) * self.rightmostpoint.horz

        self.points = self.leftmostpoint, self.rightmostpoint
        self.rotational_inertia = sum(point.rotational_inertia for point in self.points)

    def sticky(self):
        self.angular_speed *= 0.7


def skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, radius_of_both_wheels, ground_y):
    if left_wheel_center_y - radius_of_both_wheels <= ground_y:
        return True
    elif right_wheel_center_y - radius_of_both_wheels <= ground_y:
        return True
    return False

def main():
    global debug
    init_axle_x = 100
    init_axle_y = 150
    axle = axle__(init_axle_x, init_axle_y, 10)
    length = 600
    wheels_horz_d = 100
    l = line(
        axle,
        (
            point_mass_on_line(axle, length - wheels_horz_d, 20),
            point_mass_on_line(axle, -wheels_horz_d, 20)
        ),
        wheels_horz_d=wheels_horz_d,
        length=length
    )
    total_horz = abs(l.leftmostpoint.horz) + l.rightmostpoint.horz

    ground_y = 100

    t = 0
    fill = True

    fpsclock = pygame.time.Clock()
    fps_desired = 30

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

    frm_by_frm = False

    done = False
    center_x = l.leftmostpoint.x + math.cos(l.angle - rad(15)) * wheels_horz_d
    center_y = (l.leftmostpoint.y + math.sin(l.angle - rad(15)) * wheels_horz_d)

    prevent_clip_done = False
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
                if event.key == pygame.K_DOWN:
                    fps_desired -= 1
                if event.key == pygame.K_UP:
                    fps_desired += 1
                if event.key == pygame.K_d:
                    debug = not debug

                if event.key == pygame.K_ESCAPE:
                    quit()

        pygame.draw.line(display, WHITE, (0, D_HEIGHT - ground_y), (D_WIDTH, D_HEIGHT - ground_y))

        if 0 < t < 20:
            l.apply_force(Force(40, 0), 0)
            pass
        if 20 < t < 24:
            l.apply_force(Force(3000, rad(270)), l.leftmostpoint.horz)
        if 120 < t < 130:
            l.apply_force(Force(60, 0), 0)
        if 130 < t < 134:
            done = False
            l.maintain_axle(l.LEFT)
            l.apply_force(Force(3000, rad(270)), l.leftmostpoint.horz)
        if 140 < t < 165:
            l.apply_force(Force(60, l.angle + rad(270)), l.rightmostpoint.horz)

        if l.leftmostpoint.y < ground_y and not done:
            paradox = l.rightmostpoint.velocity
            wittgensteinpopper = l.leftmostpoint.velocity
            watchtower = l.axle.velocity
            done = True

            # move axle to centroid

            l.maintain_axle(line.CENT)

            l.angular_speed = 0
            l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0)
            l.apply_force(Force(get_x_y_components(wittgensteinpopper)[0] * l.leftmostpoint.mass * 0.5, rad(90)), 0)
            l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0)
            l.apply_force(Force(l.mass * paradox.magnitude / 3, paradox.direction), l.rightmostpoint.horz)

        if 20 < t < 55:
            l.apply_force(Force(60, l.angle + rad(270)), l.rightmostpoint.horz - wheels_horz_d)
            pass

        l.apply_force(Force(g_accel * l.mass, rad(270)), 0)

        if skateboard_is_in_contact_with_ground(
                left_wheel_center_y=center_y,
                right_wheel_center_y=(center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2)),
                radius_of_both_wheels=24,
                ground_y=ground_y) and not close(deg(l.angle), 0):
            # apply gravity to the leftmost and rightmost points
            l.apply_force(Force(g_accel * l.leftmostpoint.mass, rad(270)), l.leftmostpoint.horz)
            l.apply_force(Force(g_accel * l.rightmostpoint.mass, rad(270)), l.rightmostpoint.horz)

            left_wheel_bottom_y = center_y - 24
            right_wheel_bottom_y = (center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2)) - 24
            if min(left_wheel_bottom_y, right_wheel_bottom_y) == left_wheel_bottom_y:
                l.maintain_axle(l.LEFT)
            elif min(left_wheel_bottom_y, right_wheel_bottom_y) == right_wheel_bottom_y:
                l.maintain_axle(l.RIGH)

        if skateboard_is_in_contact_with_ground(
                left_wheel_center_y=center_y,
                right_wheel_center_y=(center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2)),
                radius_of_both_wheels=24,
                ground_y=ground_y) and close(deg(l.angle), 0, min_diff=2):
            l.sticky()

        if skateboard_is_in_contact_with_ground(
                left_wheel_center_y=center_y,
                right_wheel_center_y=(center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2)),
                radius_of_both_wheels=24,
                ground_y=ground_y):
            # first prevent clipping
            if not prevent_clip_done:
                left_wheel_bottom_y = center_y - 24
                right_wheel_bottom_y = (center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2)) - 24

                d = ground_y - min(left_wheel_bottom_y, right_wheel_bottom_y)

                for point in l.points:
                    point.y += d - 1
                l.axle.y += d - 1

            #display.fill(GREY)
            # make l.axle.velocity only its horizontal part
            x_mag, y_mag = get_x_y_components(l.axle.velocity)
            try:
                if extract_sign(x_mag) == 1:
                    l.axle.velocity = Velocity(x_mag, rad(0))
                elif extract_sign(x_mag) == -1:
                    l.axle.velocity = Velocity(abs(x_mag), rad(180))
            except ZeroDivisionError:
                l.axle.velocity = Velocity(0, 0)

        l.tick()


        l.draw()


        draw_text(f't={t}', 100, 100)

        center_x = l.leftmostpoint.x + math.cos(l.angle - rad(15)) * wheels_horz_d
        center_y = (l.leftmostpoint.y + math.sin(l.angle - rad(15)) * wheels_horz_d)
        pygame.draw.circle(display, WHITE, (
            center_x,
            D_HEIGHT - center_y
        ), 24, width=1)

        pygame.draw.circle(display, WHITE, (
            center_x + math.cos(l.angle) * (total_horz - wheels_horz_d * 2),
            D_HEIGHT - (center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2))
        ), 24, width=1)
        # radius of 24 px is magic number
        # so is rad(15 deg)




        draw_text(f'fps={fps_desired}', 100, 140)

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
