# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import time
import pprint
import requests
import numpy as np
import logging as log

from env import MoabEnv
from common import Vector2


class BrainNotFound(Exception):
    pass


# Controllers ------------------------------------------------------------------
def pid_controller(
    Kp=75,  # Proportional coefficient
    Ki=0.5,  # Integral coefficient
    Kd=45,  # Derivative coefficient
    max_angle=22,
    **kwargs,
):
    def next_action(state):
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y = env_state

        if ball_detected:
            action_x = Kp * x + Ki * sum_x + Kd * vel_x
            action_y = Kp * y + Ki * sum_y + Kd * vel_y
            action_x = np.clip(action_x, -max_angle, max_angle)
            action_y = np.clip(action_y, -max_angle, max_angle)

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


class BrainController:
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.
    """

    def __init__(
        self,
        max_angle=22,
        port=5555,
        client_id=12345,
        alert_fn=lambda toggle: None,
        **kwargs,
    ):
        # Test that port has a valid brain
        status = requests.get(f"http://localhost:{port}/v1/status").status_code
        valid_brain = status == 200

        if not valid_brain:
            raise ValueError(f"Port {port} is not a valid Bonsai brain")

        # Test whether the brain is v1 or v2 (also resets memory if a v2 brain)
        status = requests.delete(
            f"http://localhost:{port}/v2/clients/{client_id}"
        ).status_code
        self.version = 2 if status == 204 else 1

        if self.version == 1:
            self.prediction_url = f"http://localhost:{port}/v1/prediction"
        elif self.version == 2:
            self.prediction_url = (
                f"http://localhost:{port}/v2/clients/{client_id}/predict"
            )
        else:
            raise ValueError("Brain version `{self.version}` is not supported.")

        self.client_id = client_id
        self.max_angle = max_angle
        self.alert_fn = alert_fn
        self.port = port

    def __call__(self, state):
        env_state, ball_detected, buttons = state
        x, y, vx, vy, sum_x, sum_y = env_state

        observables = {
            "state": {"ball_x": x, "ball_y": y, "ball_vel_x": vx, "ball_vel_y": vy}
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}
        if True:  # ball_detected:

            # Trap on POST failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.post(self.prediction_url, json=observables)
                info = {"status": response.status_code, "resp": response.json()}
                action_json = response.json()

                if response.ok:
                    if self.alert_fn is not None:
                        self.alert_fn(False)

                    print(action_json)
                    if self.version == 1:
                        pitch = action_json["input_pitch"]
                        roll = action_json["input_roll"]
                    elif self.version == 2:
                        pitch = action_json["concepts"]["MoveToCenter"]["action"][
                            "input_pitch"
                        ]
                        roll = action_json["concepts"]["MoveToCenter"]["action"][
                            "input_roll"
                        ]
                    else:
                        raise ValueError(
                            f"Brain version `{self.version}` is not supported."
                        )

                    # Scale and clip
                    pitch = np.clip(
                        pitch * self.max_angle, -self.max_angle, self.max_angle
                    )
                    roll = np.clip(
                        roll * self.max_angle, -self.max_angle, self.max_angle
                    )

                    # To match how the old brain works (only integer plate angles)
                    pitch, roll = int(pitch), int(roll)

                    action = Vector2(-roll, pitch)
                else:
                    if self.alert_fn is not None:
                        self.alert_fn(True)

            except requests.exceptions.ConnectionError as e:
                print(f"No brain listening on port: {self.port}", file=sys.stderr)
                raise BrainNotFound

            except Exception as e:
                print(f"Brain exception: {e}")

        return action, info

