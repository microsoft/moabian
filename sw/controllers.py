import sys
import time
import requests
import numpy as np
import logging as log

from hat import Icon, Text
from env import MoabEnv
from common import Vector2


# Helper functions for filtering
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


# Controllers ------------------------------------------------------------------
def pid_controller(
    Kp=75,  # Proportional coefficient
    Ki=0.5,  # Integral coefficient
    Kd=45,  # Derivative coefficient
    frequency=30,
    fc=15,  # Cutoff frequency of the high pass filter (10 is overly smooth, 30 is like no filter)
    max_angle=16,
    **kwargs,
):
    # TODO: The PID controller should probably use matrices instead of 2
    #       independent SISO (single-input single-output) controls.

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
        menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
        action = Vector2(-joy_y, joy_x)
        return action * max_angle

    return next_action


def zero_controller(**kwargs):
    return lambda state: Vector2(0, 0)


def random_control(low=-1, high=1, **kwargs):
    x, y = np.random.uniform(low, high, size=2)
    return lambda state: Vector2(x, y)


def brain_controller(
    frequency=30, max_angle=22, end_point="http://localhost:5000", **kwargs
):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.
    """
    prediction_url = f"{end_point}/v1/prediction"
    prev_position = Vector2(0, 0)
    tick = 0
    prev_time = time.time()

    # Logging helper functions
    def csv_header():
        cols = ["tick", "dt", "ball_x", "ball_y", "ball_vel_x", "ball_vel_y"]
        cols = cols + ["status", "pitch", "roll"]

        with open("/tmp/log.csv", "w") as fd:
            print(cols, file=fd)

    def csv_row(tick, dt, observables, response):
        cols = ["ball_x", "ball_y", "ball_vel_x", "ball_vel_y"]

        # state vector
        s = [observables[i] for i in cols]

        # action vector
        a = [response.status_code]
        d = response.json()
        a.append(d.get("input_pitch"))  # might be None which is ok
        a.append(d.get("input_roll"))

        # combine all to a list for the log
        l = [tick, dt] + s + a

        # round floats to 5 digits
        l = [f"{n:.5f}" if type(n) is float else n for n in l]
        l = ",".join([str(e) for e in l])

        with open("/tmp/log.csv", "a") as fd:
            print(l, file=fd)

    def next_action(state):
        nonlocal prev_position  # allow prev_position to be updated in inner scope
        nonlocal tick, prev_time

        tick = tick + 1
        if tick == 1:
            csv_header()

        dt = time.time() - prev_time
        prev_time = time.time()

        ball_detected, position = state
        action = Vector2(0, 0)

        velocity = (position - prev_position) * frequency
        prev_position = position

        observables = {
            "ball_x": position.x,
            "ball_y": position.y,
            "ball_vel_x": velocity.x,
            "ball_vel_y": velocity.y,
        }

        if ball_detected:
            # Trap on GET failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.get(prediction_url, json=observables)
                action = response.json()

                csv_row(tick, dt, observables, response)

                if response.ok:
                    action = requests.get(prediction_url, json=observables).json()
                    action_pitch = action["input_pitch"]
                    action_roll = action["input_roll"]

                    # Scale and clip
                    action_pitch = np.clip(
                        action_pitch * max_angle, -max_angle, max_angle
                    )
                    action_roll = np.clip(
                        action_roll * max_angle, -max_angle, max_angle
                    )

                    action = Vector2(action_pitch, action_roll)

            except Exception as e:
                log.exception(f"Exception calling predictor\n{e}")
        return action

    return next_action
