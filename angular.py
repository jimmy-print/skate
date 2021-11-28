import pygame
from math import sin, cos, sqrt, acos
from utils import *
from phys import *
from aesthetics import draw_man

LEFTWHEEL = 'LEFTWHEEL'
RIGHTWHEEL = 'RIGHTWHEEL'

INFINITY = 10000000000000

g_accel = 0.4

wheel_radius = 12


def main():
    global debug
    init_axle_x = 100
    init_axle_y = 500
    axle = axle__(init_axle_x, init_axle_y, 10)
    length = 250
    wheels_horz_d = 50
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

    ground_y = 50

    t = 0
    fill = True

    fpsclock = pygame.time.Clock()
    fps_desired = 45

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

    l.maintain_axle(l.CENT)

    left_pop = tolstoj(5)
    right_pop = tolstoj(5)

    left_small_push = tolstoj(2)
    right_small_push = tolstoj(2)

    fake_state_machine = {
        "left_pop": left_pop,
        "right_pop": right_pop,
        "left_small_push": left_small_push,
        "right_small_push": right_small_push
    }
    while True:
        t += 1

        left_pop.iter()
        right_pop.iter()
        left_small_push.iter()
        right_small_push.iter()

        pausing_this_frm = False

        print(left_pop.cond)
        draw_text('asdfasdadf', 400, 400)

        if fill:
            display.fill(BLACK)
        draw_text(f't={t}', 100, 80)
        draw_text(str(left_pop.cond), 100, 100)

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
                if event.key == pygame.K_p:
                    debug = not debug
                if event.key == pygame.K_c and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    l.apply_force(Force(150, l.angle + rad(270)), l.rightmostpoint.horz)
                    right_small_push.do()
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    l.maintain_axle(l.RIGH)
                    l.apply_force(Force(4000, rad(270)), l.rightmostpoint.horz)

                    right_pop.do()
                if event.key == pygame.K_z and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    l.apply_force(Force(150, l.angle + rad(270)), l.leftmostpoint.horz)
                    left_small_push.do()
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    l.maintain_axle(l.LEFT)
                    l.apply_force(Force(4000, rad(270)), l.leftmostpoint.horz)

                    left_pop.do()
                if skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius,
                                                        ground_y):
                    if event.key == pygame.K_d:
                        l.apply_force(Force(100, rad(0)), 0)
                    if event.key == pygame.K_a:
                        l.apply_force(Force(100, rad(180)), 0)

                if event.key == pygame.K_ESCAPE:
                    quit()

        pygame.draw.line(display, WHITE, (0, D_HEIGHT - ground_y), (D_WIDTH, D_HEIGHT - ground_y))

        l.apply_force(Force(g_accel * l.mass, rad(270)), 0)

        center_x = l.leftmostpoint.x + math.cos(l.angle - rad(15)) * wheels_horz_d
        center_y = (l.leftmostpoint.y + math.sin(l.angle - rad(15)) * wheels_horz_d)

        left_wheel_center_y = center_y
        right_wheel_center_y = (center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2))
        left_wheel_center_x = center_x
        right_wheel_center_x = (center_x + math.cos(l.angle) * (total_horz - wheels_horz_d * 2))

        left_wheel_base_y = LEFTWHEEL, left_wheel_center_y - wheel_radius
        right_wheel_base_y = RIGHTWHEEL, right_wheel_center_y - wheel_radius
        if skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius, ground_y):
            l.apply_force(Force(g_accel * l.mass, rad(90)), 0)

            x_component = get_x_y_components(l.axle.velocity)[0]

            if x_component > 0:
                l.axle.velocity = Velocity(x_component, 0)
            elif x_component < 0:
                l.axle.velocity = Velocity(abs(x_component), rad(180))
            elif x_component == 0:
                l.axle.velocity = Velocity(0, 0)

            if not close(deg(l.angle), 0, min_diff=1.3):
                l.apply_force(Force(g_accel * l.leftmostpoint.mass, rad(270)), l.leftmostpoint.horz)
                l.apply_force(Force(g_accel * l.rightmostpoint.mass, rad(270)), l.rightmostpoint.horz)
            else:
                l.sticky()

            if min(left_wheel_base_y[1], right_wheel_base_y[1]) == left_wheel_base_y[1]:
                l.maintain_axle(l.LEFT)
            elif min(left_wheel_base_y[1], right_wheel_base_y[1]) == right_wheel_base_y[1]:
                l.maintain_axle(l.RIGH)

            d = ground_y - min(left_wheel_base_y[1], right_wheel_base_y[1])
            l.raise_uniformwise(d - 1)

        if l.leftmostpoint.y < ground_y and l.axle_loc == l.LEFT and abs(l.angular_speed) > 0:
            paradox = l.rightmostpoint.velocity
            wittgensteinpopper = l.leftmostpoint.velocity
            watchtower = l.axle.velocity

            l.maintain_axle(line.CENT)
            l.angular_speed = 0
            l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0)
            l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0, color=CYAN)
            l.apply_force(Force(l.mass * paradox.magnitude / 4, paradox.direction), l.rightmostpoint.horz)
            l.apply_force(Force(wittgensteinpopper.magnitude * 0.2 * l.mass, rad(90)), 0)

        if l.rightmostpoint.y < ground_y and l.axle_loc == l.RIGH and abs(l.angular_speed) > 0:
            paradox = l.leftmostpoint.velocity
            wittgensteinpopper = l.rightmostpoint.velocity
            watchtower = l.axle.velocity

            l.maintain_axle(line.CENT)
            l.angular_speed = 0
            l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0)
            l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0, color=CYAN)
            l.apply_force(Force(l.mass * paradox.magnitude / 4, paradox.direction), l.leftmostpoint.horz)
            l.apply_force(Force(wittgensteinpopper.magnitude * 0.2 * l.mass, rad(90)), 0)

        if l.leftmostpoint.y < ground_y and l.axle_loc == l.CENT and get_x_y_components(l.axle.velocity)[1] < 0:
            x_component = get_x_y_components(l.axle.velocity)[0]

            if x_component > 0:
                l.axle.velocity = Velocity(x_component, 0)
            elif x_component < 0:
                l.axle.velocity = Velocity(abs(x_component), rad(180))
            elif x_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.leftmostpoint.velocity.magnitude, rad(90)), l.leftmostpoint.horz)
            l.raise_uniformwise(ground_y - l.leftmostpoint.y)
            l.raise_uniformwise(5)
        if l.rightmostpoint.y < ground_y and l.axle_loc == l.CENT and get_x_y_components(l.axle.velocity)[1] < 0:
            x_component = get_x_y_components(l.axle.velocity)[0]

            if x_component > 0:
                l.axle.velocity = Velocity(x_component, 0)
            elif x_component < 0:
                l.axle.velocity = Velocity(abs(x_component), rad(180))
            elif x_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.rightmostpoint.velocity.magnitude, rad(90)), l.rightmostpoint.horz,
                          color=CYAN)
            l.raise_uniformwise(ground_y - l.rightmostpoint.y)
            l.raise_uniformwise(5)

        if l.leftmostpoint.x < 0:
            y_component = get_x_y_components(l.axle.velocity)[1]

            if y_component > 0:
                l.axle.velocity = Velocity(y_component, rad(90))
            elif y_component < 0:
                l.axle.velocity = Velocity(abs(y_component), rad(270))
            elif y_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.leftmostpoint.velocity.magnitude, rad(0)), l.leftmostpoint.horz, color=CYAN)
            l.push_left_uniformwise(5)
        if l.rightmostpoint.x < 0:
            y_component = get_x_y_components(l.axle.velocity)[1]

            if y_component > 0:
                l.axle.velocity = Velocity(y_component, rad(90))
            elif y_component < 0:
                l.axle.velocity = Velocity(abs(y_component), rad(270))
            elif y_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.rightmostpoint.velocity.magnitude, rad(0)), l.rightmostpoint.horz,
                          color=CYAN)
            l.push_left_uniformwise(5)
        if l.leftmostpoint.x > D_WIDTH:
            y_component = get_x_y_components(l.axle.velocity)[1]

            if y_component > 0:
                l.axle.velocity = Velocity(y_component, rad(90))
            elif y_component < 0:
                l.axle.velocity = Velocity(abs(y_component), rad(270))
            elif y_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.leftmostpoint.velocity.magnitude, rad(180)), l.leftmostpoint.horz,
                          color=CYAN)
            l.push_left_uniformwise(-5)
        if l.rightmostpoint.x > D_WIDTH:
            y_component = get_x_y_components(l.axle.velocity)[1]

            if y_component > 0:
                l.axle.velocity = Velocity(y_component, rad(90))
            elif y_component < 0:
                l.axle.velocity = Velocity(abs(y_component), rad(270))
            elif y_component == 0:
                l.axle.velocity = Velocity(0, 0)
            l.apply_force(Force(l.mass * l.rightmostpoint.velocity.magnitude, rad(180)), l.rightmostpoint.horz,
                          color=CYAN)
            l.push_left_uniformwise(-5)

        l.tick()

        l.draw()

        draw_man(left_wheel_top_x=left_wheel_center_x, left_wheel_top_y=left_wheel_center_y + wheel_radius,
                 right_wheel_top_x=right_wheel_center_x, right_wheel_top_y=right_wheel_center_y + wheel_radius,
                 l_angle=l.angle, wheel_horz=wheels_horz_d, board_len=length, state=fake_state_machine)

        pygame.draw.circle(display, WHITE, (
            center_x,
            D_HEIGHT - center_y
        ), wheel_radius, width=1)

        pygame.draw.circle(display, WHITE, (
            center_x + math.cos(l.angle) * (total_horz - wheels_horz_d * 2),
            D_HEIGHT - (center_y + math.sin(l.angle) * (total_horz - wheels_horz_d * 2))
        ), wheel_radius, width=1)
        # rad(15 deg) is magic number

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


if __name__ == '__main__':
    main()
