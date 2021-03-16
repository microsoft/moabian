# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import json

from typing import Tuple
from hat import Hat, Buttons
from dataclasses import dataclass, astuple
from camera import OpenCVCameraSensor
from detector import hsv_detector, meters_to_pixels
from common import high_pass_filter, low_pass_filter, derivative


@dataclass
class EnvState:
    x: float = 0.0
    y: float = 0.0
    vel_x: float = 0.0
    vel_y: float = 0.0
    sum_x: float = 0.0
    sum_y: float = 0.0

    def __iter__(self):
        return iter(astuple(self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        a = f"x,y ({self.x:.3f}, {self.y:.3f}) "
        b = f"ẋ,ẏ ({self.vel_x:.3f}, {self.vel_y:.3f}) "
        c = f"Δx,Δy {self.sum_x:.3f}, {self.sum_y:.3f})"
        return a + b + c


class MoabEnv:
    def __init__(
        self,
        frequency=30,
        debug=False,
        use_plate_angles=False,
        derivative_fn=derivative,
        calibration_file="bot.json",
    ):
        self.debug = debug
        self.frequency = frequency
        self.derivative_fn = derivative
        self.vel_x = self.derivative_fn(frequency)
        self.vel_y = self.derivative_fn(frequency)
        self.sum_x, self.sum_y = 0, 0

        self.hat = Hat(use_plate_angles=use_plate_angles, debug=debug)
        self.hat.open()
        self.camera = OpenCVCameraSensor(frequency=frequency)
        self.detector = hsv_detector(debug=debug)

        self.calibration_file = calibration_file
        self.reset_calibration()

    def __enter__(self):
        # TODO: only enable if necessary, not on enter/exit
        self.hat.enable_servos()
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.hat.lower()
        self.hat.disable_servos()
        self.hat.close()
        self.camera.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"hue: {self.hue}, offsets: {self.servo_offsets}"

    def reset_calibration(self, calibration_file=None):
        # Use default if not defined
        calibration_file = calibration_file or self.calibration_file

        # Get calibration settings
        with open(self.calibration_file, "r") as f:
            calib = json.load(f)
        plate_offsets = (calib["plate_x_offset"], calib["plate_y_offset"])
        self.plate_offsets_pixels = [int(i) for i in meters_to_pixels(plate_offsets)]
        self.servo_offsets = calib["servo_offsets"]
        self.hue = calib["ball_hue"]

        # Set the servo offsets (self.hue & self.plate_offsets_pixels are used in step)
        self.hat.set_servo_offsets(*self.servo_offsets)
        self.camera.x_offset_pixels = self.plate_offsets_pixels[0]
        self.camera.y_offset_pixels = self.plate_offsets_pixels[1]

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

        # Update derivate calulation
        vel_x, vel_y = self.vel_x(x), self.vel_y(y)
        # Update the summation (integral calculation)
        self.sum_x += x
        self.sum_y += y

        buttons = self.hat.get_buttons()
        state = EnvState(x, y, vel_x, vel_y, self.sum_x, self.sum_y)

        return state, ball_detected, buttons
