# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import json
import numpy as np

from common import Vector2
from detector import hsv_detector
from typing import Tuple, Optional
from camera import OpenCVCameraSensor
from hat import Hat, Buttons, Icon, PowerIcon


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
                "ball_hue": 44,  # Hue
                "plate_offsets": (0.0, 0.0),  # X,Y offset in meters
                "servo_offsets": (0.0, 0.0, 0.0),  # Servo angle offset in degrees
            }

        self.plate_offsets = calib["plate_offsets"]
        self.servo_offsets = calib["servo_offsets"]
        self.hue = calib["ball_hue"]

    def go_up(self):
        # Set the plate to its hover position, experimentally found to be 150
        self.set_servos(150, 150, 150)
        time.sleep(0.200)  # Give enough time for the action before turning off servos

    def go_down(self):
        # Set the plate to its lowest position, experimentally found to be 155
        self.set_servos(155, 155, 155)
        time.sleep(0.200)  # Give enough time for the action before turning off servos

    def get_buttons(self):
        # Get the buttons after doing a noop (ensure the buttons are up to date)
        self.hat.noop()
        return self.hat.get_buttons()

    def enable_servos(self):
        self.hat.enable_servos()

    def disable_servos(self):
        self.hat.disable_servos()

    def set_servos(self, s1, s2, s3):
        # Note the indexing offset
        s1 += self.servo_offsets[0]
        s2 += self.servo_offsets[1]
        s3 += self.servo_offsets[2]
        self.hat.set_servos((s1, s2, s3))

    def display(
        self,
        text: Optional[str] = None,
        icon: Optional[str] = None,
        scrolling: bool = False,
    ):
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
        s1, s2, s3 = plate_angles_to_servo_positions(pitch, roll)
        self.set_servos(s1, s2, s3)

    def step(self, pitch, roll) -> Buttons:
        self.set_angles(pitch, roll)
        frame, elapsed_time = self.camera()
        buttons = self.hat.get_buttons()
        ball_detected, (ball_center, ball_radius) = self.detector(frame, hue=self.hue)

        ball_center.x -= self.plate_offsets[0]
        ball_center.y -= self.plate_offsets[1]

        return ball_center, ball_detected, buttons, frame, elapsed_time