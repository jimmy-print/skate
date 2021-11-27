import pygame
from utils import *
from math import sin, cos

def draw_man(left_wheel_top_x, left_wheel_top_y, right_wheel_top_x, right_wheel_top_y, l_angle, wheel_horz):
    calf_and_thigh_len = 100

    midway_between_leftmostp_and_left_wheel_x = left_wheel_top_x - cos(l_angle) * (wheel_horz / 2)
    midway_between_leftmostp_and_left_wheel_y = left_wheel_top_y - sin(l_angle) * (wheel_horz / 2)

    display.fill(CYAN,
         (
             (midway_between_leftmostp_and_left_wheel_x,
              D_HEIGHT - midway_between_leftmostp_and_left_wheel_y),
             (10, 10)
         )
     )

    midway_between_rightmostp_and_right_wheel_x = right_wheel_top_x + cos(l_angle) * (wheel_horz / 2)
    midway_between_rightmostp_and_right_wheel_y = right_wheel_top_y + sin(l_angle) * (wheel_horz / 2)

    display.fill(CYAN,
         (
             (midway_between_rightmostp_and_right_wheel_x,
              D_HEIGHT - midway_between_rightmostp_and_right_wheel_y),
             (10, 10)
         )
     )

    midway_left = (midway_between_leftmostp_and_left_wheel_x, midway_between_leftmostp_and_left_wheel_y)




    
    pygame.draw.line(
        display,
        GREY,
        (midway_left[0], D_HEIGHT - midway_left[1]),
        (midway_left[0], D_HEIGHT - (midway_left[1] + 100)))
