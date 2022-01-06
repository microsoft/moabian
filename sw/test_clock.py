#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import time
import argparse
import requests
import numpy as np
import logging as log

from env import *
from hat import Buttons
from common import Vector2
from controllers import BrainNotFound


def main(port=5000):
    f = brain_controller(port=port)
    state = EnvState(x=0.1, y=0.1)

    t0 = time.time()
    # Hit the brain prediction as fast as possible for 5 seconds (at 30 Hz)
    print(f"Testing brain at port {port}")
    try:
        for x in range(1, 30 * 5):
            a, i = f(state)
            # print(i)
        dt = time.time() - t0
        print(f"{dt/5*1000:0.1f} msec out of 1000 msec")

    except Exception as ex:
        print(ex)
        sys.exit(1)


def brain_controller(
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
    prediction_url = f"http://localhost:{port}/v1/prediction"

    def next_action(state):
        x, y, vel_x, vel_y, sum_x, sum_y = state

        observables = {
            "ball_x": x,
            "ball_y": y,
            "ball_vel_x": vel_x,
            "ball_vel_y": vel_y,
        }

        action = Vector2(0, 0)  # Action is 0,0 if not detected or brain didn't work
        info = {"status": 400, "resp": ""}

        # Trap on GET failures so we can restart the brain without
        # bringing down this run loop. Plate will default to level
        # when it loses the connection.
        try:
            # Get action from brain
            response = requests.get(prediction_url, json=observables)
            info = {"status": response.status_code, "resp": response.json()}
            action_json = response.json()

            if response.ok:
                action_json = requests.get(prediction_url, json=observables).json()
                pitch = action_json["input_pitch"]
                roll = action_json["input_roll"]

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

    return next_action


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", metavar="port", type=int, help="port for brain to test")
    args = parser.parse_args()
    main(port=args.port)
