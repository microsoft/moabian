import time
import numpy as np

from hat import Icon, Text
from env import MoabEnv
from common import Vector2


def _high_pass_filter(frequency, fc=50, return_reset=False):
    x_dot_cstate = 0
    frequency = frequency
    fc = fc

    def next_action(x):
        nonlocal x_dot_cstate  # allow x_dot_cstate to be updated in inner scope
        x_dot = -(fc ** 2) * x_dot_cstate + fc * x
        x_dot_cstate += (-fc * x_dot_cstate + x) / frequency
        return x_dot

    return next_action


def _derivative(requency, fc=None):
    last_x = 0
    dt = 1 / frequency

    def next_action(x):
        return (x - last_x) * dt

    return next_action


def pid_controller(
    Kp=0.15,  # / 2.375,  # Proportional coefficient
    Ki=0.001,  # / 2.375,  # Integral coefficient
    Kd=0.090,  # / 2.375,  # Derivative coefficient
    frequency=30,
    fc=15,  # Cutoff frequency of the high pass filter (10 is overly smooth, 30 is like no filter)
    max_angle=16,
    **kwargs,
):
    # TODO: The PID controller should probably use matrices instead of 2
    #       independent SISO (single-input single-output) controls.
    Kp = Kp
    Ki = Ki
    Kd = Kd
    fc = fc
    frequency = frequency
    max_angle = max_angle

    # Use a high pass filter instead of a numerical derivative for stability.
    # A high pass filtered signal can be thought of as a derivative of a low
    # pass filtered signal: fc*s / (s + fc) = fc*s * 1 / (s + fc)
    # For more info: https://en.wikipedia.org/wiki/Differentiator
    # Or: https://www.youtube.com/user/ControlLectures/
    hpf_x = _high_pass_filter(frequency, fc)
    hpf_y = _high_pass_filter(frequency, fc)

    sum_x = 0
    sum_y = 0

    def next_action(state):
        nonlocal sum_x, sum_y  # allow sum_x and sum_y to be updated in inner scope

        ball_detected, position = state
        x, y = position
        print(position)

        if ball_detected:
            action_x = Kp * x + Ki * sum_x + Kd * hpf_x(x)
            action_y = Kp * y + Ki * sum_y + Kd * hpf_y(y)
            action_x = np.clip(action_x, -max_angle, max_angle)
            action_y = np.clip(action_y, -max_angle, max_angle)
            # Update the integral term
            sum_x += x
            sum_y += y

            # NOTE the flipped X & Y! (and the inverted second term)
            action = Vector2(action_y, -action_x)
        else:
            # Move plate back to flat
            action = Vector2(0, 0)

        return action

    return next_action


def manual_controller(hat=None, max_angle=22, **kwargs):
    assert hat is not None

    def next_action(state):
        ball_detected, position = state
        print("Ball at:", position)

        menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
        action = Vector2(-joy_y, joy_x)
        return action * max_angle

    return next_action


def zero_controller(**kwargs):
    return lambda state: Vector2(0, 0)


def random_control(low=-1, high=1, **kwargs):
    x, y = np.random.uniform(low, high, size=2)
    return lambda state: Vector2(x, y)
