# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from hardware import MoabHardware
from typing import Tuple, Optional
from dataclasses import dataclass, astuple
from hat import Hat, Buttons, Icon, PowerIcon
from common import high_pass_filter, low_pass_filter, derivative


@dataclass
class EnvState:
    x: float = 0.0
    y: float = 0.0
    vel_x: float = 0.0
    vel_y: float = 0.0
    sum_x: float = 0.0
    sum_y: float = 0.0
    bonsai_episode_status: int = 0

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
            calibration_file=calibration_file,
        )

    def __enter__(self):
        self.hardware.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.hardware.__exit__(type, value, traceback)

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
        self.bonsai_episode_status = 0

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

        state = EnvState(x, y, vel_x, vel_y, self.sum_x, self.sum_y, self.bonsai_episode_status)

        return state, ball_detected, buttons
