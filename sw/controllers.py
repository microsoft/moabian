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


def _brain_controller(
    max_angle=22,
    port=5555,
    alert_fn=lambda toggle: None,
    **kwargs,
):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.
    """

    #prediction_url = f"http://localhost:{port}/v1/prediction"
    prediction_url = f"http://localhost:{port}/v2/clients/12345/predict"

    def next_action(state):
        env_state, ball_detected, buttons = state
        x, y, vx, vy, sum_x, sum_y = env_state

        observables = {
            "state": {
                "ball_x": x,
                "ball_y": y,
                "ball_vel_x": vx,
                "ball_vel_y": vy
            }
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}
        if ball_detected:

            # Trap on POST failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.post(prediction_url, json=observables)
                info = {"status": response.status_code, "resp": response.json()}
                action_json = response.json()

                if response.ok:
                    if alert_fn is not None:
                        alert_fn(False)

                    pitch = action_json["concepts"]["MoveToCenter"]["action"]["input_pitch"]
                    roll = action_json["concepts"]["MoveToCenter"]["action"]["input_roll"]

                    # Scale and clip
                    pitch = np.clip(pitch * max_angle, -max_angle, max_angle)
                    roll = np.clip(roll * max_angle, -max_angle, max_angle)

                    # To match how the old brain works (only integer plate angles)
                    pitch, roll = int(pitch), int(roll)

                    action = Vector2(-roll, pitch)
                else:
                    if alert_fn is not None:
                        alert_fn(True)

            except requests.exceptions.ConnectionError as e:
                print(f"No brain listening on port: {port}", file=sys.stderr)
                raise BrainNotFound

            except Exception as e:
                print(f"Brain exception: {e}")

        return action, info

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
        status = requests.delete(f"http://localhost:{port}/v2/clients/{client_id}").status_code
        self.version = 2 if status == 204 else 1

        if self.version == 1:
            self.prediction_url = f"http://localhost:{port}/v1/prediction"
        elif self.version == 2:
            self.prediction_url = f"http://localhost:{port}/v2/clients/{client_id}/predict"
        else:
            raise ValueError("Brain version `{self.version}` is not supported.")

        print(self.prediction_url)

        self.client_id = client_id
        self.max_angle = max_angle
        self.alert_fn = alert_fn
        self.port = port

    def __call__(self, state):
        env_state, ball_detected, buttons = state
        x, y, vx, vy, sum_x, sum_y = env_state

        observables = {
            "state": {
                "ball_x": x,
                "ball_y": y,
                "ball_vel_x": vx,
                "ball_vel_y": vy
            }
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}
        if True:#ball_detected:

            # Trap on POST failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.post(self.prediction_url, json=observables)
                info = {"status": response.status_code, "resp": response.json()}
                action_json = response.json()

                print(f"\n\n\nResponse: {repsonse}, \naction_json:\n{action_json}")

                if response.ok:
                    if self.alert_fn is not None:
                        self.alert_fn(False)

                    print(action_json)
                    if self.version == 1:
                        pitch = action_json["input_pitch"]
                        roll = action_json["input_roll"]
                    elif self.version == 2:
                        pitch = action_json["concepts"]["MoveToCenter"]["action"]["input_pitch"]
                        roll = action_json["concepts"]["MoveToCenter"]["action"]["input_roll"]
                    else:
                        raise ValueError(f"Brain version `{self.version}` is not supported.")

                    # Scale and clip
                    pitch = np.clip(pitch * self.max_angle, -self.max_angle, self.max_angle)
                    roll = np.clip(roll * self.max_angle, -self.max_angle, self.max_angle)

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


def brain_pid_hybrid_controller(
    max_angle=22,
    port=5000,
    alert_fn=lambda toggle: None,
    **kwargs,
):
    brain_fn = _brain_controller(port=port, **kwargs)
    pid_fn = pid_controller(**kwargs)

    def next_action(state):
        (x, y, vx, vy, _, _), ball_detected, buttons = state
        observables = {
            "state": {
                "ball_x": x,
                "ball_y": y,
                "ball_vel_x": vx,
                "ball_vel_y": vy
            }
        }

        try:
            return brain_fn(state)
        except:
            return pid_fn(state)

    return next_action

def brain_controller_quick_switch(
    max_angle=22,
    port=5000,
    alert_fn=lambda toggle: None,
    **kwargs,
):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.

    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.


    This works the same as brain controller but will switch between a pair of two
    ports depending on which one is active/working.

    If port is a single number the spillover is port + 1.
    """
    if isinstance(port, tuple):
        port1, port2 = port
    elif isinstance(int(port), int):
        port1, port2 = int(port), int(port) + 1
    else:
        raise ValueError(f"{port} must be an int or a tuple of ints")

    port1_controller_fn = _brain_controller(port=port1, **kwargs)
    port2_controller_fn = _brain_controller(port=port2, **kwargs)
    pid_controller_fn = pid_controller(**kwargs)

    #prediction_url1 = f"http://localhost:{port1}/v1/prediction"
    #prediction_url2 = f"http://localhost:{port2}/v1/prediction"

    prediction_url1 = f"http://localhost:{port}/v2/clients/12345/predict"
    prediction_url2 = f"http://localhost:{port}/v2/clients/12345/predict"

    current_controller = 1  # Start by trying the first port

    def next_action(state):
        nonlocal current_controller
        (x, y, vx, vy, _, _), ball_detected, buttons = state
        observables = {
            "state": {
                "ball_x": x,
                "ball_y": y,
                "ball_vel_x": vx,
                "ball_vel_y": vy
            }
        }

        try:
            if current_controller == 1:
                return port1_controller_fn(state)
            else:
                return port2_controller_fn(state)
        except:
            if current_controller == 1:
                current_controller = 2
            else:
                current_controller = 1

            # Note: just getting here requires you to run brain controller...
            #       so the timing even when fallling back to pid is going to be
            #       longer than usual.
            # If neither port works fall back to PID controller
            return pid_controller_fn(state)

    return next_action

def forget_memory(
    url: str = "http://localhost:5000/v2/clients/{clientId}"
):
    # Reset the Memory vector because exported brains don't understand episodes 
    response = requests.delete(url)
    if response.status_code == 204:
        print('Resetting Memory vector in exported brain...')
    else:
        print('Error: {}'.format(response.status_code))


# Export as the default brain controller
#brain_controller = brain_controller_quick_switch
#brain_controller = brain_pid_hybrid_controller
brain_controller = _brain_controller


