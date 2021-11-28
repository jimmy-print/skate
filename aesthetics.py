import pygame
from utils import *
from math import sin, cos


def draw_man(left_wheel_top_x, left_wheel_top_y, right_wheel_top_x, right_wheel_top_y, l_angle, wheel_horz, board_len,
             state):
    def draw_line(p0, p1, color):
        pygame.draw.line(display, color, (p0[0], D_HEIGHT - p0[1]), (p1[0], D_HEIGHT - p1[1]))

    centroid = (
        left_wheel_top_x + cos(l_angle) * (board_len - wheel_horz * 2) / 2,
        left_wheel_top_y + sin(l_angle) * (board_len - wheel_horz * 2) / 2
    )

    vert = 175
    hip_point = [
        centroid[0], centroid[1] + vert]

    if state["left_pop"].cond:
        hip_point[1] -= 25

    display.fill(GREEN, ((hip_point[0], D_HEIGHT - hip_point[1]), (10, 10)))


    if state["left_pop"].cond:
        draw_line(hip_point, (
            hip_point[0] - 50,
            hip_point[1] - 75
        ), GREY)
        draw_line((
            hip_point[0] - 50,
            hip_point[1] - 75
        ), (left_wheel_top_x, left_wheel_top_y), GREY)
    elif state["left_small_push"].cond:
        slightly_further_left = (
            left_wheel_top_x - math.cos(l_angle) * wheel_horz / 2,
            left_wheel_top_y + math.sin(l_angle) * wheel_horz / 2
        )
        draw_line(hip_point, slightly_further_left, GREY)
    else:
        draw_line(hip_point, (left_wheel_top_x, left_wheel_top_y), GREY)

    if state["right_pop"].cond:
        draw_line(hip_point, (
            hip_point[0] + 50,
            hip_point[1] - 75
        ), GREY)
        draw_line((
            hip_point[0] + 50,
            hip_point[1] - 75
        ), (right_wheel_top_x, right_wheel_top_y), GREY)
    elif state["right_small_push"].cond:
        slightly_further_right = (
            right_wheel_top_x + math.cos(l_angle) * wheel_horz / 2,
            right_wheel_top_y + math.sin(l_angle) * wheel_horz / 2
        )
        draw_line(hip_point, slightly_further_right, GREY)
    else:
        draw_line(hip_point, (right_wheel_top_x, right_wheel_top_y), GREY)


    head_point = (
        hip_point[0], hip_point[1] + vert * 1.25)

    display.fill(GREEN, ((head_point[0], D_HEIGHT - head_point[1]), (10, 10)))

    draw_line(hip_point, head_point, GREY)


    left_hand_point = (
        head_point[0] - board_len / 2,
        head_point[1] - 200)
    right_hand_point = (
        head_point[0] + board_len / 2,
        head_point[1] - 200)

    draw_line(head_point, left_hand_point, GREY)
    draw_line(head_point, right_hand_point, GREY)

    head_radius = 40
    pygame.draw.circle(display, GREY, (head_point[0], D_HEIGHT - (head_point[1] + head_radius)), head_radius, width=1)
