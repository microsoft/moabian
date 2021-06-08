# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import json
import numpy as np

from typing import Tuple, Optional
from hat import Hat, Buttons, Icon, PowerIcon
from camera import OpenCVCameraSensor
from dataclasses import dataclass, astuple
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


def plate_angles_to_servo_positions(
    pitch: float,
    roll: float,
    arm_len: float = 55.0,
    side_len: float = 170.87,
    pivot_height: float = 80.0,
    angle_max: float = 160,
    angle_min: float = 90,
) -> Tuple[float, float, float]:
    servo_angles = [0.0, 0.0, 0.0]

    z1 = pivot_height + np.sin(np.radians(roll)) * (side_len / np.sqrt(3))
    r = pivot_height - np.sin(np.radians(roll)) * (side_len / (2 * np.sqrt(3)))
    z2 = r + np.sin(np.radians(-pitch)) * (side_len / 2)
    z3 = r - np.sin(np.radians(-pitch)) * (side_len / 2)

    if z1 > 2 * arm_len:
        z1 = 2 * arm_len
    if z2 > 2 * arm_len:
        z2 = 2 * arm_len
    if z3 > 2 * arm_len:
        z3 = 2 * arm_len

    servo_angles[0] = 180 - (np.degrees(np.arcsin(z1 / (2 * arm_len))))
    servo_angles[1] = 180 - (np.degrees(np.arcsin(z2 / (2 * arm_len))))
    servo_angles[2] = 180 - (np.degrees(np.arcsin(z3 / (2 * arm_len))))

    servo_angles = np.clip(servo_angles, angle_min, angle_max)
    return servo_angles


class MoabHardware:
    def __init__(
        self,
        frequency=30,
        debug=False,
        verbose=0,
        derivative_fn=derivative,
        calibration_file="bot.json",
    ):
        self.debug = debug
        self.verbose = verbose
        self.frequency = frequency

        self.hat = Hat(debug=debug, verbose=verbose)
        self.hat.open()
        self.camera = OpenCVCameraSensor(frequency=frequency)
        self.detector = hsv_detector(debug=debug)

        # Set the calibration
        self.calibration_file = calibration_file
        self.reset_calibration()

    def __enter__(self):
        self.camera.start()
        return self

    def __exit__(self, type, value, traceback):
        self.go_down()
        self.hat.disable_servos()
        self.hat.display_power_symbol("TO WAKE", PowerIcon.POWER)
        self.hat.close()
        self.camera.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"hue: {self.hue}, servo offsets: {self.servo_offsets}, plate offsets: {self.plate_offsets}"

    def reset_calibration(self, calibration_file=None):
        # Use default if not defined
        calibration_file = calibration_file or self.calibration_file

        # Get calibration settings
        if os.path.isfile(calibration_file):
            with open(calibration_file, "r") as f:
                calib = json.load(f)
        else:  # Use defaults
            calib = {
                "ball_hue": 44,
                "plate_offsets": (0.0, 0.0),
                "servo_offsets": (0.0, 0.0, 0.0),
            }

        self.plate_offsets = calib["plate_offsets"]
        self.servo_offsets = calib["servo_offsets"]
        self.hue = calib["ball_hue"]


    def display(self, text: Optional[str]=None, icon: Optional[str]=None, scrolling: bool=False):
        # Optionally display the controller active text
        if icon and text:
            if scrolling:
                raise ValueError("Cannot display scrolling screen with an icon")
            self.hat.display_string_icon(text, icon)
        elif text:
            if scrolling:
                self.hat.display_long_string(text)
            else:
                self.hat.display_string(text)

    def set_angles(self, pitch, roll):
        servo_positions = plate_angles_to_servo_positions(pitch, roll)
        self.hat.set_servos(servo_positions, offsets=self.servo_offsets)

    def go_up(self):
        """
        Set the plate to its hover position.
        This was experimentally found to be 150 (down but still leaving some
        space at the bottom).
        """
        self.hat.set_servos((150, 150, 150))
        time.sleep(0.200)  # Give enough time for the action to be taken before turning off servos

    def go_down(self):
        """
        Set the plate to its lower position (usually powered-off state).
        This was experimentally found to be 155 (lowest possible position).
        """
        self.hat.set_servos((155, 155, 155))
        time.sleep(0.200)  # Give enough time for the action to be taken before turning off servos

    def step(self, pitch, roll) -> Buttons:
        self.set_angles(pitch, roll)
        frame, elapsed_time = self.camera()
        buttons = self.hat.get_buttons()        
        ball_detected, (ball_center, ball_radius) = self.detector(frame, hue=self.hue)
        return ball_center, ball_detected, buttons


class MoabEnv:
    def __init__(
        self,
        frequency=30,
        debug=False,
        verbose=0,
        derivative_fn=derivative,
        calibration_file="bot.json",
    ):
        self.debug = debug
        self.verbose = verbose
        self.frequency = frequency
        self.derivative_fn = derivative
        self.vel_x = self.derivative_fn(frequency)
        self.vel_y = self.derivative_fn(frequency)
        self.sum_x, self.sum_y = 0, 0

        self.hardware = MoabHardware(
            frequency=frequency,
            debug=debug,
            verbose=verbose,
            derivative_fn=derivative_fn,
            calibration_file=calibration_file
        )

        self.calibration_file = calibration_file
        self.reset_calibration()

    def __enter__(self):
        self.hardware.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.hardware.__exit__(type, value, traceback)

    def reset_calibration(self, calibration_file=None):
        self.hardware.reset_calibration(calibration_file)

    def reset(self, text=None, icon=None):
        # Optionally display the controller active text
        self.hardware.display(text, icon)

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
        pitch, roll = action
        (x, y), ball_detected, buttons = self.hardware.step(pitch, roll)

        # Update derivate calulation
        vel_x, vel_y = self.vel_x(x), self.vel_y(y)
        # Update the summation (integral calculation)
        self.sum_x += x
        self.sum_y += y

        state = EnvState(x, y, vel_x, vel_y, self.sum_x, self.sum_y)

        return state, ball_detected, buttons
