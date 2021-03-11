# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import json

from hat import Hat
from typing import Tuple
from dataclasses import dataclass
from common import EnvState, Buttons
from detector import hsv_detector as detector
from camera import OpenCVCameraSensor as Camera
from common import high_pass_filter, low_pass_filter, derivative


class MoabEnv:
    def __init__(
        self,
        frequency=30,
        debug=False,
        use_plate_angles=False,
        derivative_fn=derivative,
        calibration_file="bot.json",
    ):
        # Get calibration settings
        with open(calibration_file, "r") as f:
            calib = json.load(f)
        self.plate_offsets = calib["plate_x_offset"], calib["plate_y_offset"]
        self.servo_offsets = calib["servo_offsets"]
        self.hue = calib["ball_hue"]

        self.hat = Hat(use_plate_angles=use_plate_angles, debug=debug)
        self.hat.open()
        self.hat.set_servo_offsets(*self.servo_offsets)
        self.camera = Camera(frequency=frequency)
        self.detector = detector(debug=debug, hue=self.hue)
        self.debug = debug

        self.frequency = frequency
        self.derivative_fn = derivative
        self.vel_x = self.derivative_fn(frequency)
        self.vel_y = self.derivative_fn(frequency)
        self.sum_x, self.sum_y = 0, 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'hue: {self.hue}, offsets: {self.servo_offsets}'


    def __enter__(self):
        self.hat.enable_servos()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower()
        self.hat.disable_servos()
        self.hat.close()
        self.camera.stop()

    def reset_calibration(self, calibration_file="bot.json"):
        # Get calibration settings
        with open(calibration_file, "r") as f:
            calib = json.load(f)
        self.plate_offsets = calib["plate_x_offset"], calib["plate_y_offset"]
        self.servo_offsets = calib["servo_offsets"]
        self.hue = calib["ball_hue"]
        # Set the servo offsets (self.hue & self.plate_offsets are used in step)
        self.hat.set_servo_offsets(*self.servo_offsets)

    def reset(self, text=None, icon=None):
        # Optionally display the controller active text
        if icon and text:
            self.hat.display_string_icon(text, icon)
        elif text:
            self.hat.display_string(text)

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

    def step(self, action) -> Tuple[EnvState, bool, Buttons]:
        plate_x, plate_y = action
        self.hat.set_angles(plate_x, plate_y)

        frame, elapsed_time = self.camera()
        ball_detected, cicle_feature = self.detector(frame, hue=self.hue)
        ball_center, ball_radius = cicle_feature

        x, y = ball_center

        # TODO: this is temporary solution to centering the ball. This should
        #       really be used to figure out the correct camera cropping!!!
        x -= self.plate_offsets[0]
        y -= self.plate_offsets[1]

        # Update derivate calulation
        vel_x, vel_y = self.vel_x(x), self.vel_y(y)
        # Update the summation (integral calculation)
        self.sum_x += x
        self.sum_y += y

        buttons = self.hat.get_buttons()
        state = EnvState(x, y, vel_x, vel_y, self.sum_x, self.sum_y)

        return state, ball_detected, buttons
