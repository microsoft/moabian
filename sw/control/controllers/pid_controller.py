# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
PID Controller

proportional–integral–derivative feed-back algorithm to control
the plate angles.
"""

import time
import numpy as np
from typing import Dict
from enum import IntEnum
from dataclasses import dataclass
from control.hat import interface as pymoab

from ..common import IController, IDevice, CircleFeature, Vector2


class Axis(IntEnum):
    X = 0
    Y = 1


class HighPassFilter(object):
    def __init__(self, frequency, fc=50):
        self.x_dot_cstate = 0
        self.frequency = frequency
        self.fc = fc

    def reset(self):
        self.x_dot_cstate = 0

    def __call__(self, x):
        x_dot = -(self.fc ** 2) * self.x_dot_cstate + self.fc * x
        self.x_dot_cstate += (-self.fc * self.x_dot_cstate + x) / self.frequency
        return x_dot


class PIDController(IController):
    """PID controller class.

    This class handles the classic control calculations for ball balancing when
    in vision mode. In general, the following formulas are used for calculating
    appropriate values:

    # -----------------------------------------
    # Find velocity            | velocity_x = (previous_x - current_x) / elapsedSec
    # Predict position         | predicted_x = current_x + (velocity_x * time_step_future)
    # Find new error           | error_prediction = set_point_x - predicted_x
    # Set previous error point | error_prediction_prev = error_prediction
    # Sum of errors            | sum_error_prediction += error_prediction
    # -----------------------------------------

    """

    @dataclass
    class Config(IController.Config):
        Kp: float = 0.15
        Ki: float = 0.001
        Kd: float = 0.090
        conversionFactor: float = 2.375
        fc: float = 15  # Cutoff frequency of the high pass filter
        frequency: float = 30

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config

        self.velocity = [0, 0]
        self.set_point = [0, 0]
        self.predicted = [0, 0]
        self.prev_position = [0, 0]
        self.error_prediction = [0, 0]
        self.sum_error_prediction = [0.0, 0.0]
        self.lastElapsedMs = 0

        # Use a high pass filter instead of a numerical derivative for stability
        filter_x = HighPassFilter(self.config.frequency, self.config.fc)
        filter_y = HighPassFilter(self.config.frequency, self.config.fc)
        self.filters = [filter_x, filter_y]

    def determine_theta(self, elapsedSec: float, position: float, axis: Axis) -> float:
        """Calculate desired angle of plate to balance ball.

        Args:
            position ([int, int]): The current x,y position of the ball.
            elapsedSec (float): The interval of time that has elapsed.
            axis (int): The axis in which to calulate (0 = x, 1 = y)

        Returns:
            Calculated angle to balance ball.

        """
        prod = np.clip(
            self.config.Kp * position, -self.config.maxAngle, self.config.maxAngle
        )
        inte = np.clip(
            self.config.Ki * self.sum_error_prediction[axis],
            -self.config.maxAngle,
            self.config.maxAngle,
        )
        # High pass filtered signal can be thought of as a derivative of a low
        # pass filtered signal: fc*s / (s + fc) = fc*s * 1 / (s + fc)
        # For more info: https://en.wikipedia.org/wiki/Differentiator
        # Or: https://www.youtube.com/user/ControlLectures/
        derv = np.clip(
            self.config.Kd * self.filters[axis](position),
            -self.config.maxAngle,
            self.config.maxAngle,
        )
        theta = prod + inte + derv
        theta_final = np.clip(theta, -self.config.maxAngle, self.config.maxAngle)

        self.sum_error_prediction[axis] += position
        return theta_final

    def detector_to_controller_units(self, ball_pos: Vector2) -> Vector2:
        return ball_pos / self.config.conversionFactor

    def on_menu_down(self, sender: IDevice):
        sender.stop()

        # Hover the plate and deactivate the servos
        pymoab.hover_plate()
        pymoab.time.sleep(0.5)
        pymoab.disable_servo_power()
        pymoab.time.sleep(0.5)

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        """Calculate plate adjustment values based on current position to balance ball.

        Returns:
            Adjusted (theta) x,y values resulting from calculations.
        """
        ball = detectorResults.get("ball")
        if ball:
            # Calculate plate position using controller-specific factors
            ball_pos_real = self.detector_to_controller_units(ball.center)

            Tx = self.determine_theta(elapsedSec, ball_pos_real.y, Axis.Y)
            Ty = -self.determine_theta(elapsedSec, ball_pos_real.x, Axis.X)

            return Vector2(Tx, Ty)
        else:
            return Vector2(0, 0)
