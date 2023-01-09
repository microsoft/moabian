# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import time
import requests
import numpy as np
import logging as log

from enum import IntEnum
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


def dump_ball_controller(angle=90, tilt_angle=16, **kwargs):
    """Dump the ball towards angle."""

    def next_action(state):
        env_state, ball_detected, buttons = state
        a = -tilt_angle * np.cos(np.radians(angle))
        b = -tilt_angle * np.sin(np.radians(angle))
        action = Vector2(a, b)
        return action, {}

    return next_action


def zero_controller(**kwargs):
    def next_action(state):
        return Vector2(0.0, 0.0), {}

    return next_action


def nn_controller(filepath="train_moab_weights.npz", **kwargs):
    npz = np.load(filepath)
    w0 = npz["w0"]
    b0 = npz["b0"]
    w1 = npz["w1"]
    b1 = npz["b1"]
    w_out = npz["w_out"]

    def next_action(state):
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y = env_state
        state = np.array([x, y, vel_x, vel_y])
        action = w_out @ np.tanh(w1 @ np.tanh(w0 @ state + b0) + b1)

        action = np.clip(action * 22, -22, 22)
        pitch, roll = action

        if ball_detected:
            # New sims match the coordinates of old sim for compatibility
            return Vector2(-roll, pitch), {}
        else:
            return Vector2(0, 0), {}

    return next_action


def brain_controller(
    max_angle=22,
    port=5555,
    client_id=123,
    alert_fn=None,
    **kwargs,
):
    """
    This class interfaces with an HTTP server running locally.
    It passes the current hardware state and gets new plate
    angles in return.
    The hardware state is unprojected from camera pixel space
    back to real space by using the calculated plate surface plane.

    Note: Still use v1 endpoint even if it's a v2 brain because on every new
    creation of a brain controller we still call DELETE on the v2 brain
    endpoint. This way we don't need to know information about what the trained
    brain was called to navigate the json response.
    """
    # Reset memory if a v2 brain
    status = requests.delete(f"http://localhost:{port}/v2/clients/{client_id}")
    version = 2 if status.status_code == 204 else 1

    if version == 1:
        prediction_url = f"http://localhost:{port}/v1/prediction"
    elif version == 2:
        prediction_url = f"http://localhost:{port}/v2/clients/{client_id}/predict"
    else:
        raise ValueError("Brain version `{self.version}` is not supported.")

    def next_action_v1(state):
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

                if response.ok:
                    pitch = info["resp"]["input_pitch"]
                    roll = info["resp"]["input_roll"]

                    # Scale and clip
                    pitch = np.clip(pitch * max_angle, -max_angle, max_angle)
                    roll = np.clip(roll * max_angle, -max_angle, max_angle)

                    # To match how the old brain works (only integer plate angles)
                    pitch, roll = int(pitch), int(roll)
                    action = Vector2(-roll, pitch)

            except requests.exceptions.ConnectionError as e:
                print(f"No brain listening on port: {port}", file=sys.stderr)
                raise BrainNotFound
            except Exception as e:
                print(f"Brain exception: {e}")
        return action, info

    def next_action_v2(state):
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y = env_state

        observables = {
            "state": {
                "ball_x": x,
                "ball_y": y,
                "ball_vel_x": vel_x,
                "ball_vel_y": vel_y,
            }
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}
        if ball_detected:

            # Trap on GET failures so we can restart the brain without
            # bringing down this run loop. Plate will default to level
            # when it loses the connection.
            try:
                # Get action from brain
                response = requests.post(prediction_url, json=observables)
                info = {"status": response.status_code, "resp": response.json()}

                if response.ok:
                    concepts = info["resp"]["concepts"]
                    concept_name = list(concepts.keys())[0]  # Just use first concept
                    pitch = concepts[concept_name]["action"]["input_pitch"]
                    roll = concepts[concept_name]["action"]["input_roll"]

                    # Scale and clip
                    pitch = np.clip(pitch * max_angle, -max_angle, max_angle)
                    roll = np.clip(roll * max_angle, -max_angle, max_angle)

                    # To match how the old brain works (only integer plate angles)
                    pitch, roll = int(pitch), int(roll)
                    action = Vector2(-roll, pitch)

            except requests.exceptions.ConnectionError as e:
                print(f"No brain listening on port: {port}", file=sys.stderr)
                raise BrainNotFound
            except Exception as e:
                print(f"Brain exception: {e}")
        return action, info

    if version == 1:
        return next_action_v1
    elif version == 2:
        return next_action_v2
    else:
        raise ValueError("Brain version `{self.version}` is not supported.")


def kiosk_mode_decorator(
    controller,
    controller_kwargs,
    env,
    timeout=15,
    dump_location_clock_hand=2,
):
    # Define state machine states
    class KioskMode(IntEnum):
        CONTROLLER = 0
        DUMPING = 1
        IDLE = 2

    # Convert from hour hand location to degrees
    dump_angle = ((-dump_location_clock_hand + 3) * (360 / 12)) % 360
    dump_time = 1  # Take 1 second to dump the ball

    controller_fn = controller(**controller_kwargs)
    dump_ball_fn = dump_ball_controller(angle=dump_angle, tilt_angle=5)
    zero_fn = zero_controller()

    mode = KioskMode.CONTROLLER
    mode_start_time = time.time()  # Time since you started in the current mode
    ball_continuously_detected_count = 0  # For idle mode to ensure no false balls

    def next_action(state):
        nonlocal mode, mode_start_time, ball_continuously_detected_count
        _, ball_detected, _ = state

        if mode == KioskMode.CONTROLLER:
            if time.time() > mode_start_time + timeout:
                mode = KioskMode.DUMPING
                mode_start_time = time.time()
            return controller_fn(state)

        elif mode == KioskMode.DUMPING:
            if time.time() > mode_start_time + dump_time:
                mode = KioskMode.IDLE
                mode_start_time = time.time()

                # Level the plate then disable servos
                env.step([0, 0])
                env.hardware.disable_servos()
                time.sleep(1 / env.frequency)

            if ball_detected:
                return dump_ball_fn(state)
            else:
                return zero_fn(state)

        elif mode == KioskMode.IDLE:
            if ball_detected:
                ball_continuously_detected_count += 1
            if ball_continuously_detected_count >= 3:
                env.hardware.enable_servos()
                time.sleep(1 / env.frequency)
                mode = KioskMode.CONTROLLER
                mode_start_time = time.time()
                ball_continuously_detected_count = 0
            return zero_fn(state)

        else:
            raise ValueError(f"Mode: `{mode}` is invalid")

    return next_action
