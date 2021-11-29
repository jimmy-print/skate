import pygame
from math import sin, cos, sqrt, acos
import utils
from utils import *
from phys import *
from aesthetics import draw_man
from textbox import TextBox
import json
import pathlib
import glob

LEFTWHEEL = 'LEFTWHEEL'
RIGHTWHEEL = 'RIGHTWHEEL'

INFINITY = 10000000000000

g_accel = 0.4

wheel_radius = 12


def draw_available_files(currently_playing, playing):
    i = 0
    draw_text('Recorded tricks:', stage_width + 20, 300)
    goteem = False
    for f in glob.glob("tricks/*.json"):
        i += 1
        ff = f[7:len(f)].split('.')[0]

        draw_text(ff, stage_width + 60, 300 + i * 40)

        r = pygame.Rect(stage_width + 20, 300 + i * 40, 30, 30)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if in_rect(mouse_x, mouse_y, r):
            pygame.draw.rect(display, lighter(KINDADARKGREY), r)
            if pygame.mouse.get_pressed()[0]:
                goteem = True
                thingy = f
        else:
            pygame.draw.rect(display, KINDADARKGREY, r)


        pygame.draw.polygon(display, GREEN, ((stage_width + 20 + 5, 300 + i * 40 + 5), (stage_width + 20 + 5, 300 + i * 40 + 30 - 5), (stage_width + 20 + 30 - 5, 300 + i * 40 + 15)))

    if playing:
        return currently_playing

    if goteem:
        return thingy

def main():
    ground_y = 50 + (D_HEIGHT - stage_height)

    init_axle_x = 50
    init_axle_y = ground_y - wheel_radius * 2
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

    def stop_recording():
        input = TextBox((stage_width + margin, D_HEIGHT - margin * 20, 150, 30), command=lambda _, __: None, clear_on_enter=True, inactive_on_enter=False)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    if event.key == pygame.K_RETURN:
                        return ''.join(input.buffer)
                if event.type == pygame.QUIT:
                    quit()
                input.get_event(event)

            input.update()
            input.draw(display)

            pygame.display.update()


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

    recording = False

    dat = []
    tmp = {}

    recording_area_height = D_HEIGHT - stage_height
    num_of_actions = 6
    each_bar_height = recording_area_height / num_of_actions
    def convert_dat_to_rects(dat):
        for t, states in dat:
            for movement in states:
                if states[movement]:
                    if movement == 'left_small_push':
                        yield pygame.Rect(t + 220, stage_height, 1, each_bar_height), RED
                    elif movement == 'right_small_push':
                        yield pygame.Rect(t + 220, stage_height + 1 * each_bar_height, 1, each_bar_height), GREEN
                    elif movement == 'left_pop':
                        yield pygame.Rect(t + 220, stage_height + 2 * each_bar_height, 1, each_bar_height), YELLOW
                    elif movement == 'right_pop':
                        yield pygame.Rect(t + 220, stage_height + 3 * each_bar_height, 1, each_bar_height), BLUE
                    elif movement == 'left_push':
                        yield pygame.Rect(t + 220, stage_height + 4 * each_bar_height, 1, each_bar_height), CYAN
                    elif movement == 'right_push':
                        yield pygame.Rect(t + 220, stage_height + 5 * each_bar_height, 1, each_bar_height), MAGENTA
                    else:
                        raise RuntimeError(f'state contains invalid movement \'{movement}\', at t={t}')

    playing = False
    currently_playing = None
    current_dat = []
    current_rects = []
    done = False

    while True:
        t += 1

        left_pop.iter()
        right_pop.iter()
        left_small_push.iter()
        right_small_push.iter()

        tmp = {}

        tmp["right_small_push"] = False
        tmp["left_small_push"] = False
        tmp["right_pop"] = False
        tmp["left_pop"] = False
        tmp["left_push"] = False
        tmp["right_push"] = False

        pausing_this_frm = False

        if fill:
            display.fill(WHITE)
        pygame.draw.rect(display, BLACK, ((0, 0, stage_width, stage_height)))
        pygame.draw.rect(display, KINDADARKGREY, ((0, 0 + stage_height, D_WIDTH - (D_WIDTH - stage_width), D_HEIGHT - (D_HEIGHT - stage_height))))

        draw_text(f't={t}', 100, 100)
        draw_text(f'Recording: {recording}', 100, 80)
        draw_text(f'Playing: {playing}, {currently_playing}', 100, 60)


        mouse_x, mouse_y = pygame.mouse.get_pos()

        if recording:
            pygame.draw.rect(display, WHITE, ((t + 220, 0 + stage_height, 1, D_HEIGHT - (D_HEIGHT - stage_height))))
        draw_text(f'Push down left side (z)', 10, D_HEIGHT - (D_HEIGHT - stage_height))
        draw_text(f'Push down right side (c)', 10, D_HEIGHT - (D_HEIGHT - stage_height) + 1 * each_bar_height)
        draw_text(f'Pop left side (shift+z)', 10, D_HEIGHT - (D_HEIGHT - stage_height) + 2 * each_bar_height)
        draw_text(f'Pop right side (shift+c)', 10, D_HEIGHT - (D_HEIGHT - stage_height) + 3 * each_bar_height)
        draw_text(f'Move left (a)', 10, D_HEIGHT - (D_HEIGHT - stage_height) + 4 * each_bar_height)
        draw_text(f'Move right (d)', 10, D_HEIGHT - (D_HEIGHT - stage_height) + 5 * each_bar_height)


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
                    utils.debug = not utils.debug

                if not playing:
                    if event.key == pygame.K_c and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        l.apply_force(Force(150, l.angle + rad(270)), l.rightmostpoint.horz)
                        right_small_push.do()

                        tmp["right_small_push"] = True
                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        l.maintain_axle(l.RIGH)
                        l.apply_force(Force(4000, rad(270)), l.rightmostpoint.horz)

                        right_pop.do()

                        tmp["right_pop"] = True
                    if event.key == pygame.K_z and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        l.apply_force(Force(150, l.angle + rad(270)), l.leftmostpoint.horz)
                        left_small_push.do()

                        tmp["left_small_push"] = True
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        l.maintain_axle(l.LEFT)
                        l.apply_force(Force(4000, rad(270)), l.leftmostpoint.horz)

                        left_pop.do()

                        tmp["left_pop"] = True
                    if skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius,
                                                            ground_y):
                        if event.key == pygame.K_d:
                            l.apply_force(Force(100, rad(0)), 0)
                            tmp["right_push"] = True
                        if event.key == pygame.K_a:
                            l.apply_force(Force(100, rad(180)), 0)
                            tmp["left_push"] = True

                if event.key == pygame.K_ESCAPE:
                    quit()

        print(current_dat)
        if playing:
            pygame.draw.rect(display, WHITE, ((t + 220, 0 + stage_height, 1, D_HEIGHT - (D_HEIGHT - stage_height))))

            for rect, color in current_rects:
                pygame.draw.rect(display, color, rect)

            try:
                if current_dat[t][1]['right_small_push']:
                    l.apply_force(Force(150, l.angle + rad(270)), l.rightmostpoint.horz)
                    right_small_push.do()
                elif current_dat[t][1]['left_small_push']:
                    l.apply_force(Force(150, l.angle + rad(270)), l.leftmostpoint.horz)
                    left_small_push.do()
                elif current_dat[t][1]['right_pop']:
                    l.maintain_axle(l.RIGH)
                    l.apply_force(Force(4000, rad(270)), l.rightmostpoint.horz)

                    right_pop.do()
                elif current_dat[t][1]['left_pop']:
                    l.maintain_axle(l.LEFT)
                    l.apply_force(Force(4000, rad(270)), l.leftmostpoint.horz)

                    left_pop.do()
                elif current_dat[t][1]['right_push']:
                    if skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius,
                                                                ground_y):
                        l.apply_force(Force(100, rad(0)), 0)
                elif current_dat[t][1]['left_push']:
                    if skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius,
                                                                ground_y):
                        l.apply_force(Force(100, rad(180)), 0)
            except IndexError:
                playing = False
                currently_playing = None
                done = False

        dat.append((t, tmp))
        if recording:
            for rect, color in convert_dat_to_rects(dat):
                pygame.draw.rect(display, color, rect)

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
        if l.leftmostpoint.x > stage_width:
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
        if l.rightmostpoint.x > stage_width:
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

        pygame.draw.rect(display, DARKGREY, ((stage_width, 0, 1000, 1000)))

        margin = 30
        button_width = 30
        button_height = 30

        currently_playing = draw_available_files(currently_playing=currently_playing, playing=playing)
        if currently_playing is not None and not recording and not done:
            done = True
            l.leftmostpoint.x = 0
            l.leftmostpoint.y = ground_y + wheel_radius * 2
            l.leftmostpoint.horz = -wheels_horz_d
            l.leftmostpoint.rotational_inertia = l.leftmostpoint.mass * l.leftmostpoint.horz ** 2

            l.rightmostpoint.x = l.leftmostpoint.x + length
            l.rightmostpoint.y = ground_y + wheel_radius * 2
            l.rightmostpoint.horz = wheels_horz_d + length - wheels_horz_d * 2
            l.rightmostpoint.rotational_inertia = l.rightmostpoint.mass * l.rightmostpoint.horz ** 2

            l.axle.x = l.leftmostpoint.x + wheels_horz_d
            l.axle.y = ground_y + wheel_radius * 2
            l.axle.velocity = Velocity(0, 0)
            l.angular_speed = 0

            l.angle = 0
            t = 0
            playing = True

            with open(currently_playing) as f:
                current_dat = json.load(f)
        current_rects = convert_dat_to_rects(current_dat)


        record_button_rect = pygame.Rect(
            stage_width + margin, 0 + margin,
            button_width, button_height)
        if in_rect(mouse_x, mouse_y, record_button_rect):
            pygame.draw.rect(display, lighter(KINDADARKGREY), record_button_rect)
            pygame.draw.circle(display, RED,
                               (record_button_rect[0] + button_width / 2, record_button_rect[1] + button_height / 2),
                               button_width / 4)
            if pygame.mouse.get_pressed()[0]:
                l.leftmostpoint.x = 0
                l.leftmostpoint.y = ground_y + wheel_radius * 2
                l.leftmostpoint.horz = -wheels_horz_d
                l.leftmostpoint.rotational_inertia = l.leftmostpoint.mass * l.leftmostpoint.horz ** 2

                l.rightmostpoint.x = l.leftmostpoint.x + length
                l.rightmostpoint.y = ground_y + wheel_radius * 2
                l.rightmostpoint.horz = wheels_horz_d + length - wheels_horz_d * 2
                l.rightmostpoint.rotational_inertia = l.rightmostpoint.mass * l.rightmostpoint.horz ** 2

                l.axle.x = l.leftmostpoint.x + wheels_horz_d
                l.axle.y = ground_y + wheel_radius * 2
                l.axle.velocity = Velocity(0, 0)
                l.angular_speed = 0

                l.angle = 0
                t = 0

                recording = True
                playing = False

                dat = []
        else:
            pygame.draw.rect(display, KINDADARKGREY, record_button_rect)
            pygame.draw.circle(display, RED,
                               (record_button_rect[0] + button_width / 2, record_button_rect[1] + button_height / 2),
                               button_width / 4)

        stop_button_rect = pygame.Rect(
            record_button_rect[0] + button_width + margin / 2,
            record_button_rect[1],
            button_width, button_height)
        if in_rect(mouse_x, mouse_y, stop_button_rect):
            pygame.draw.rect(display, lighter(KINDADARKGREY), stop_button_rect)
            pygame.draw.rect(display, lighter(GREY), (
            stop_button_rect[0] + button_width / 4, stop_button_rect[1] + button_height / 4, button_width / 2,
            button_height / 2))
            if pygame.mouse.get_pressed()[0] and recording:
                filenamefirstpart = stop_recording()
                recording = False
                l.leftmostpoint.x = 0
                l.leftmostpoint.y = ground_y + wheel_radius * 2
                l.leftmostpoint.horz = -wheels_horz_d
                l.leftmostpoint.rotational_inertia = l.leftmostpoint.mass * l.leftmostpoint.horz ** 2

                l.rightmostpoint.x = l.leftmostpoint.x + length
                l.rightmostpoint.y = ground_y + wheel_radius * 2
                l.rightmostpoint.horz = wheels_horz_d + length - wheels_horz_d * 2
                l.rightmostpoint.rotational_inertia = l.rightmostpoint.mass * l.rightmostpoint.horz ** 2

                l.axle.x = l.leftmostpoint.x + wheels_horz_d
                l.axle.y = ground_y + wheel_radius * 2
                l.axle.velocity = Velocity(0, 0)
                l.angular_speed = 0

                l.angle = 0
                t = 0

                with open(f'tricks/{filenamefirstpart}.json', 'w') as f:
                    json.dump(dat, f)

                dat = []

                done = False
        else:
            pygame.draw.rect(display, KINDADARKGREY, stop_button_rect)
            pygame.draw.rect(display, GREY, (
            stop_button_rect[0] + button_width / 4, stop_button_rect[1] + button_height / 4, button_width / 2,
            button_height / 2))


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
