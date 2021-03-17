# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import requests
import numpy as np
import logging as log

from env import MoabEnv
from common import Vector2


# Controllers ------------------------------------------------------------------
def pid_controller(
    Kp=75,  # Proportional coefficient
    Ki=0.5,  # Integral coefficient
    Kd=45,  # Derivative coefficient
    max_angle=20,
    **kwargs,
):
    def next_action(state):
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y = env_state

        if ball_detected:
            # TODO: The PID controller should probably use matrices instead of 2
            #       independent SISO (single-input single-output) controls.
            action_x = Kp * x + Ki * sum_x + Kd * vel_x
            action_y = Kp * y + Ki * sum_y + Kd * vel_y
            action_x = np.clip(action_x, -max_angle, max_angle)
            action_y = np.clip(action_y, -max_angle, max_angle)

            # NOTE the flipped X & Y! (and the inverted second term)
            # TODO: fix this in next firmware rev
            action = Vector2(action_x, action_y)

        else:
            # Move plate back to flat
            action = Vector2(0, 0)

        return action, {}

    return next_action


def joystick_controller(max_angle=16, **kwargs):
    def next_action(state):
        env_state, ball_detected, buttons = state
        action = Vector2(-buttons.joy_x, -buttons.joy_y)
        return action * max_angle, {}

    return next_action


def brain_controller(
    max_angle=22,
    port=5555,
    enable_logging=False,
   # alert_fn=lambda toggle: None,
    **kwargs,
):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.
    """
    prediction_url = f"http://localhost:{port}/v1/prediction"
    print(f"{prediction_url}")

    def next_action(state):
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y = env_state

        observables = {
            "ball_x": x,
            "ball_y": y,
            "ball_vel_x": vel_x,
            "ball_vel_y": vel_y,
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}
        if ball_detected:

            # Trap on GET failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.get(prediction_url, json=observables)
                info = {"status": response.status_code, "resp": response.json()}
                action_json = response.json()

                if response.ok:
                    alert_fn(False)
                    action_json = requests.get(prediction_url, json=observables).json()
                    pitch = action_json["input_pitch"]
                    roll = action_json["input_roll"]

                    # Scale and clip
                    pitch = np.clip(pitch * max_angle, -max_angle, max_angle)
                    roll = np.clip(roll * max_angle, -max_angle, max_angle)

                    # To match how the old brain works (only integer plate angles)
                    pitch, roll = int(pitch), int(roll)

                    action = Vector2(-roll, pitch)
                else:
                    alert_fn(True)

            except Exception as e:
                log.exception(f"Exception calling predictor\n{e}")


        return action, info

    return next_action
