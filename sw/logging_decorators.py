import time
import logging as log

from common import Vector2


def logging_decorator(fn, logfile="/tmp/log.csv"):
    # Add the header line
    cols = ["tick", "dt"]  # Timing
    cols += ["x", "y", "vel_x", "vel_y"]  # State
    cols += ["pitch", "roll"]  # Action
    cols += ["status", "error_response"]  # Error status

    with open(logfile, "w") as fd:
        print(cols, file=fd)

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

        # Deconstuct the state to get the values we want
        ball_detected, (x, y, vel_x, vel_y, sum_x, sum_y) = state
        # Deconstruct action
        pitch, roll = action
        # combine all to a list for the log
        l = [tick, dt] + [x, y, vel_x, vel_y] + [pitch, roll] + [status, resp]

        # combine all to a list for the log
        # l = [tick, dt] + state + action + [status + resp]

        # round floats to 5 digits
        l = [f"{n:.5f}" if type(n) is float else n for n in l]

        # Convert all fields into strings
        l = ",".join([str(e) for e in l])

        with open(logfile, "a") as fd:
            print(l, file=fd)

        return action, info

    return decorated_fn
