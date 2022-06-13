# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import logging as log
import pandas as pd
import numpy as np
import pdb

from common import Vector2


def log_decorator(fn, logfile="/tmp/log.csv"):
    # Add the header line
    cols = ["tick", "dt"]  # Timing
    cols += ["x", "y", "vel_x", "vel_y"]  # State
    cols += ["pitch", "roll"]  # Action
    cols += ["status", "error_response"]  # Error status
    cols += ["bonsai_episode_status", "input_pitch", "input_roll"]


    header = ",".join(cols)
    with open(logfile, "w") as fd:
        print(header, file=fd)

    # Create the state variables
    prev_time = time.time()
    tick = -1  # Start at -1 since we do += 1 at the top (keep all updates together)

    # Acts like a normal controller function
    def decorated_fn(state):
        nonlocal prev_time, tick
        dt = time.time() - prev_time
        prev_time = time.time()
        tick += 1

        # Run the actual controller
        action, info = fn(state)

        # If the status and resp are in the dictionary, save them, otherwise
        # use default values of 200 and empty string
        status = info.get("status") or 200
        resp = info.get("resp") or ""

        resp = '"' + str(resp) + '"'

        # Deconstuct the state to get the values we want
        env_state, ball_detected, buttons = state
        x, y, vel_x, vel_y, sum_x, sum_y, bonsai_episode_status = env_state
        # Deconstruct action
        pitch, roll = action

        # Brain actions for logging. Purposefully swapping to match sim
        input_pitch = roll / 22
        input_roll = -pitch / 22 

        # combine all to a list for the log
        l = [tick, dt] + [x, y, vel_x, vel_y] + [pitch, roll] + [status, resp] + [bonsai_episode_status, input_pitch, input_roll]
        row = [tick, dt] + [x, y, vel_x, vel_y] + [pitch, roll] + [status, resp] + [bonsai_episode_status, input_pitch, input_roll]

        # combine all to a list for the log
        # l = [tick, dt] + state + action + [status + resp]

        # round floats to 5 digits
        l = [f"{n:8.5f}" if type(n) is float else n for n in l]

        # Convert all fields into strings
        l = ",".join([str(e) for e in l])
        
        # Append to file depending on episode terminal or not
        if bonsai_episode_status == 2:
            df = pd.read_csv(logfile)
            last_x_abs = abs(float(df['x'].iloc[-1]))
            last_y_abs = abs(float(df['y'].iloc[-1]))

            # Check what the latest csv value was and clip
            if float(df['x'].iloc[-1]) > 0.1125:
                row[2] = df['x'].iloc[-1]
            elif float(df['x'].iloc[-1]) <= 0.1125:
                if row[2] == 0:
                    if last_x_abs - last_y_abs > 0:
                        row[2] = 0.1125 * np.sign(df['x'].iloc[-1])
                    else:
                        row[2] = float(df['x'].iloc[-1])
                else:
                    pass
            
            if float(df['y'].iloc[-1]) > 0.1125:
                row[3] = df['y'].iloc[-1]
            elif float(df['y'].iloc[-1]) <= 0.1125:
                if row[3] == 0:
                    if last_y_abs - last_x_abs > 0:
                        row[3] = 0.1125 * np.sign(df['y'].iloc[-1])
                    else:
                        row[3] = float(df['y'].iloc[-1])
                else:
                    pass
            del df
            
            row = [f"{n:8.5f}" if type(n) is float else n for n in row]
            row = ",".join([str(e) for e in row])
            
            # Append final iteration when ball is missing
            with open(logfile, "a") as fd:
                print(row, file=fd)
        else:
            with open(logfile, "a") as fd:
                print(l, file=fd)

        return action, info

    return decorated_fn
