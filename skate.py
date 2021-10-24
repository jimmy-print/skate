import pygame
from pygame.locals import *

D_WIDTH, D_HEIGHT = 1280, 720
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))

pygame.font.init()
font = pygame.font.Font("inconsolata.ttf", 15)

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

x = 10
y = 400
mass = 1

g_accel = 0.05

VERT = 'VERT'
HORZ = 'HORZ'

y_velocity = 0
x_velocity = 0

ground = 300

class Direction:
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
        return f'F{self.name} {self.direction.sign} * {self.magnitude} N {self.direction.XY}'

Fw = Force(g_accel * mass, Direction(sign=-1, XY=VERT), name="weight")
#Fn = Force(Fw.magnitude, Direction(sign=Fw.direction.sign * -1, XY=Fw.direction.XY))
# TODO: ^ add function for reverse forces
Fa = Force(2, Direction(sign=1, XY=HORZ), name="x-axis applied force")
Fya = Force(5, Direction(sign=1, XY=VERT), name="y-axis applied force")

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

def draw_forces(y_forces__, x_forces__):
    for force in y_forces__:
        if force.name == "applied":
            color = RED
        else:
            color = WHITE

        s = font.render(f'F{force.name} {force.magnitude} N', True, WHITE)

        if force.direction.sign == 1:
            height = 100
            pygame.draw.rect(display, color, (x, (D_HEIGHT - y) - height, 5, height))
            display.blit(s, (x + 10, D_HEIGHT - y - height / 2))
        elif force.direction.sign == -1:
            height = 100
            pygame.draw.rect(display, color, (x, D_HEIGHT - y, 5, height))
            display.blit(s, (x + 10, D_HEIGHT - y + height / 2))

    for force in x_forces__:
        if force.name == "applied":
            color = RED
        else:
            color = WHITE

        s = font.render(f'F{force.name} {force.magnitude} N', True, WHITE)

        if force.direction.sign == 1:
            width = 100
            pygame.draw.rect(display, color, (x + width / 10, (D_HEIGHT - y), width, 5))
            display.blit(s, (x + width / 8, D_HEIGHT - y - width / 5))
        elif force.direction.sign == -1:
            width = 100
            pygame.draw.rect(display, color, (x - width, (D_HEIGHT - y), width, 5))
            display.blit(s, (x - s.get_rect().width - width / 8, D_HEIGHT - y - width / 5))

def main():
    global x_velocity, y_velocity
    global x_forces, y_forces
    global x, y

    applied = False
    y_applied = False

    t = 0

    FPS = 60
    clock = pygame.time.Clock()

    while True:
        display.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                return

        y_forces.append(Fw)

        if not y_applied:
            y_forces.append(Fya)
            y_applied = True

        if y <= ground:
            if y_velocity != 0:
                y_velocity = 0
                y = ground

            Fn = Force(Fw.magnitude, Direction(sign=Fw.direction.sign * -1, XY=Fw.direction.XY), name="normal")
            y_forces.append(Fn)
            # Ffriction = coefficient of friction * normal force
            if abs(x_velocity) > 0.0001:
                Ff = Force(Fn.magnitude * 0.5, Direction(sign=-x_velocity / abs(x_velocity), XY=HORZ), name="friction")
                x_forces.append(Ff)
            else:
                x_velocity = 0

        s = font.render(f't={t}', True, WHITE)
        display.blit(s, (10, 10))
        t += 1
        if 260 == t:
            x_forces.append(Force(x_velocity * mass, Direction(sign=-1, XY=HORZ), name="applied"))
        if 260 < t < 280:
            x_forces.append(Force(0.35, Direction(sign=1, XY=HORZ), name="applied"))
            y_forces.append(Force(0.35, Direction(sign=1, XY=VERT), name="applied"))

        y_accel = get_net_force(y_forces) / mass
        y_velocity += y_accel
        y += y_velocity

        if not applied:
            x_forces.append(Fa)
            applied = True

        x_accel = get_net_force(x_forces) / mass
        x_velocity += x_accel

        pygame.draw.rect(display, WHITE, (0, D_HEIGHT - ground, D_WIDTH, 1))

        draw_forces(y_forces, x_forces)  # place this function call after previous three lines,
        # to prevent the placement of arrows and object being out of sync

        if x >= D_WIDTH or x < 0:
            x_velocity = -x_velocity

        display.blit(font.render(f'x_accel = {x_accel}', True, WHITE), (10, 150))
        display.blit(font.render(f'x_velocity = {x_velocity}', True, WHITE), (10, 100))


        x += x_velocity
        x_forces = []
        y_forces = []

        display.blit(font.render(f'y = {y}', True, WHITE), (10, 200))

        pygame.draw.rect(display, WHITE, (x, D_HEIGHT - y, 10, 10))



        pygame.display.update()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
