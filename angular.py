import pygame
import math
import utils

VERT = 'VERT'
HORZ = 'HORZ'

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
        return f'F{self.name} {self.direction.sign} * {self.magnitude} N {self.direction}'


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

        assert utils.all_same([point.y for point in self.points])
        assert utils.all_unique([point.x for point in self.points])

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

        if utils.deg(self.angle) > 360:
            self.angle = utils.rad(utils.deg(self.angle) - 360)

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
                start = stop - utils.rad(self.handover_force)

            elif self.handover_radial_distance < 0:
                start = self.angle + utils.rad(180)
                stop = start + utils.rad(self.handover_force)

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

    y_velocity = 0
    x_velocity = 0
    y_forces = []
    x_forces = []

    def pause():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
                if event.type == pygame.QUIT:
                    quit()

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

        y_forces.append(Force(g_accel * l.mass, TwoAxisDirection(sign=-1, XY=VERT), name="vert"))
        if 0 < t < 90:
            x_forces.append(Force(0.2, TwoAxisDirection(sign=1, XY=HORZ), name="applied"))
            y_forces.append(Force(2, TwoAxisDirection(sign=1, XY=VERT), name="applied"))
        y_accel = get_net_force(y_forces) / l.mass
        y_velocity += y_accel
        l.axle[1] += y_velocity
        x_accel = get_net_force(x_forces) / l.mass
        x_velocity += x_accel
        l.axle[0] += x_velocity

        draw_forces(y_forces__=y_forces, x_forces__=x_forces, y=l.axle[1], x=l.axle[0])

        l.angular_acceleration = 0

        if 0 < t < 20:
            l.apply_force(-10, -200)

        l.tick()
        l.draw()

        l.reset_handovers()

        y_forces = []
        x_forces = []

        draw_text(f'θ={round(utils.deg(l.angle))}', 100, 100)

        pygame.display.update()
        fpsclock.tick(fps_desired)


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


if __name__ == '__main__':
    main()
