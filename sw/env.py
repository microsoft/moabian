# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time

from hat import Hat
from typing import List, Bool
from dataclasses import dataclass
from detector import hsv_detector as detector
from camera import OpenCVCameraSensor as Camera
from common import high_pass_filter, low_pass_filter, derivative

@dataclass
class Info:
    ball_detected: bool
    menu_button: bool
    joy_button: bool
    joy_x: float
    joy_y: float

@dataclass
class State:
    x: float
    y: float
    vel_x: float
    vel_y: float
    sum_x: float
    sum_y: float

class MoabEnv:
    def __init__(
        self,
        hat=None,
        frequency=30,
        debug=False,
        use_plate_angles=False,
        derivative_fn=derivative,
    ):
        if hat:
            # For cases like manual control where the hat needs to be shared
            self.hat = hat
        else:
            self.hat = Hat(use_plate_angles=use_plate_angles)
        self.camera = Camera(frequency=frequency)
        self.detector = detector(debug=debug)
        self.debug = debug

        self.frequency = frequency
        self.dt = 1 / frequency
        self.prev_time = time.time()

        # self.derivative_fn = derivative
        self.derivative_fn = lambda freq: high_pass_filter(freq, fc=15)

        self.vel_x, self.vel_y = None, None
        self.sum_x, self.sum_y = 0, 0

    def __enter__(self):
        self.hat.enable_servos()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower()
        self.hat.disable_servos()
        self.hat.close()
        self.camera.stop()

    def reset(self, control_icon=None, control_name=None):
        if control_icon and control_name:
            self.hat.set_icon_text(control_icon, control_name)

        # Reset the derivative of the position
        # Use a high pass filter instead of a numerical derivative for stability.
        # A high pass filtered signal can be thought of as a derivative of a low
        # pass filtered signal: fc*s / (s + fc) = fc*s * 1 / (s + fc)
        # For more info: https://en.wikipedia.org/wiki/Differentiator
        # Or: https://www.youtube.com/user/ControlLectures/
        self.vel_x = self.derivative_fn(self.frequency)
        self.vel_y = self.derivative_fn(self.frequency)

        # Reset the integral of the position
        self.sum_x, self.sum_y = 0, 0

        # Return the state after a step with no motor actions
        return self.step((0, 0))

    def step(self, action):
        plate_x, plate_y = action
        self.hat.set_angles(plate_x, plate_y)

        frame, elapsed_time = self.camera()
        ball_detected, cicle_feature = self.detector(frame)
        ball_center, ball_radius = cicle_feature

        x, y = ball_center
        # Update derivate calulation
        vel_x, vel_y = self.vel_x(x), self.vel_y(y)
        # Update the summation (integral calculation)
        self.sum_x += x
        self.sum_y += y

        buttons = self.hat.poll_buttons()

        return ball_detected, (x, y, vel_x, vel_y, self.sum_x, self.sum_y), buttons





