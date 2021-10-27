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


g_accel = 0.05


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


class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class line:
    def __init__(self, axlex, axley, points):  # TODO clean up data entry
        self.axle = point(axlex, axley)

        def make_point_tuple(orig_horz_d_from_axle, mass):
            return [point(self.axle.x + orig_horz_d_from_axle, self.axle.y), mass, orig_horz_d_from_axle]

        self.points = [
            make_point_tuple(point__[0], point__[1]) for point__ in points
        ]

        assert utils.all_same([tup[0].y for tup in self.points])
        assert utils.all_unique([tup[0].x for tup in self.points])

        smallest = self.points[0]
        for point__ in self.points:
            if point__[2] < smallest[2]:
                smallest = point__
        self.leftmostpoint = smallest
        largest = self.points[0]
        for point__ in self.points:
            if point__[2] > largest[2]:
                largest = point__
        self.rightmostpoint = largest

        self.angle = 0
        self.angular_acceleration = 0
        self.angular_speed = 0

        self.rotational_inertia = sum(
            (tup[1] * tup[2] ** 2) for tup in self.points
        )

        self.mass = sum(
            tup[1] for tup in self.points
        )

    def apply_force(self, force, radial_distance):
        # radial distance meaning length along the radius, not sure what the proper term is.
        # DOES NOT MEAN 'RELATING TO RADIAN'
        # if radial_distance is positive number that means towards the right, negative means left

        ANGLE_DIFF = 5
        display.fill(GREEN, ((self.axle.x + math.cos(self.angle + utils.rad(-1 * ANGLE_DIFF * utils.extract_sign(radial_distance) * utils.extract_sign(force))) * radial_distance,
                              D_HEIGHT - (self.axle.y + math.sin(self.angle + utils.rad(-1 * ANGLE_DIFF * utils.extract_sign(radial_distance) * utils.extract_sign(force))) * radial_distance)), (10, 10)))

        torque = force * radial_distance

        self.angular_acceleration = torque / self.rotational_inertia
        self.angular_speed += self.angular_acceleration

    def tick(self):
        self.angle += self.angular_speed  # should still be in radians at this point

        if utils.deg(self.angle) > 360:
            self.angle = utils.rad(utils.deg(self.angle) - 360)

        for point in self.points:
            orig_horz_distance_from_axle = point[2]
            pointdx = math.cos(self.angle) * orig_horz_distance_from_axle
            pointdy = math.sin(self.angle) * orig_horz_distance_from_axle

            point[0].x = self.axle.x + pointdx
            point[0].y = self.axle.y + pointdy

    def draw(self):
        '''
        # draw relative cartesian axiss
        pygame.draw.line(display, WHITE, (self.axle.x, D_HEIGHT), (self.axle.x, 0))
        pygame.draw.line(display, WHITE, (D_WIDTH, D_HEIGHT - self.axle.y), (0, D_HEIGHT - self.axle.y))
        '''

        # draw entire line
        pygame.draw.line(display, WHITE, (self.leftmostpoint[0].x, D_HEIGHT - self.leftmostpoint[0].y),
                         (self.rightmostpoint[0].x, D_HEIGHT - self.rightmostpoint[0].y))

        # draw axle
        axle_width = 10
        axle_height = 10
        display.fill(WHITE, ((self.axle.x, D_HEIGHT - self.axle.y), (axle_width, axle_height)))

        # draw individual points
        point_draw_width = 5
        point_draw_height = 5

        for point in self.points:
            display.fill(RED, ((point[0].x, D_HEIGHT - point[0].y), (point_draw_width, point_draw_height)))


l = line(200, 200, ((200, 10), (-200, 10)))

D_WIDTH, D_HEIGHT = 1600, 900
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.SysFont("Ubuntu", 15)

fpsclock = pygame.time.Clock()
fps_desired = 60



def main():

    t = 0
    fill = True

    y_accel = 0
    x_accel = 0
    y_velocity = 0
    x_velocity = 0
    y_forces = []
    x_forces = []

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

        y_forces.append(Force(g_accel * l.mass, TwoAxisDirection(sign=-1, XY=VERT), name="vert"))
        if 0 < t < 120:
            x_forces.append(Force(0.2, TwoAxisDirection(sign=1, XY=HORZ), name="applied"))
            y_forces.append(Force(2, TwoAxisDirection(sign=1, XY=VERT), name="applied"))
        y_accel = get_net_force(y_forces) / l.mass
        y_velocity += y_accel
        l.axle.y += y_velocity
        x_accel = get_net_force(x_forces) / l.mass
        x_velocity += x_accel
        l.axle.x += x_velocity

        draw_forces(y_forces__=y_forces, x_forces__=x_forces, y=l.axle.y, x=l.axle.x)

        l.angular_acceleration = 0

        if 0 < t < 120:
            l.apply_force(-1, -200)

        if 220 < t < 300:
            l.apply_force(-1, 200)

        l.tick()
        l.draw()

        y_forces = []
        x_forces = []

        pygame.display.update()
        fpsclock.tick(fps_desired)


def draw_text(s, x, y):
    display.blit(font.render(s, True, WHITE), (x, y))


if __name__ == '__main__':
    main()
