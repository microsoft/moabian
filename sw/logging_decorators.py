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
        action_and_possible_resp = fn(state)

        # If there is an error response it will save the status code and error
        # response, otherwise staus is 200, and resp is empty string
        if type(action_and_possible_resp) == Vector2:
            action = action_and_possible_resp
            # These two lines match a response for the brain with no errors
            status = 200
            resp = ""
        else:
            action, response = action_and_possible_resp
            # For the brain
            status = response.status_code
            resp = response.json()

        # State contains a tuple of (ball_detected, state_tuple)
        ball_detected, state_tuple = state
        # combine all to a list for the log
        l = [tick, dt] + list(state_tuple) + list(action) + [status, resp]

        # combine all to a list for the log
        # l = [tick, dt] + state + action + [status + resp]

        # round floats to 5 digits
        l = [f"{n:.5f}" if type(n) is float else n for n in l]

        # Convert all fields into strings
        l = ",".join([str(e) for e in l])

        with open(logfile, "a") as fd:
            print(l, file=fd)

        return action

    return decorated_fn
