# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Calibration Controller

Performs calibration for hue, center of camera position, and servo offsets
"""

import os
import time
import json
import numpy as np
import logging as log

from env import MoabEnv
from common import Vector2
from controllers import pid_controller
from hat import Hat, Icon, Text, plate_angles_to_servo_positions


def ball_close_enough(x, y, radius, max_ball_dist=0.2, min_ball_dist=0.05):
    # reject balls which are too far from the center and too small
    return (
        np.abs(x) < max_ball_dist
        and np.abs(y) < max_ball_dist
        and radius > min_ball_dist
    )


def calibrate_hue(camera_fn, detector_fn, hue_low=0, hue_high=255, hue_steps=20):
    img_frame, elapsed_time = camera_fn()
    hue_options = list(np.linspace(hue_low, hue_high, hue_steps))

    detected_hues = []
    for hue in hue_options:
        ball_detected, ((x, y), radius) = detector_fn(img_frame, hue=hue)

        # If we found a ball roughly in the center that is large enough
        if ball_detected and ball_close_enough(x, y, radius):
            detected_hues.append(hue)

    if len(detected_hues) > 0:
        max_hue = max(detected_hues)
        min_hue = min(detected_hues)
        avg_hue = int((max_hue + min_hue) / 2)

        log.info(f"Hue range: [{min_hue} .. {max_hue}]")
        print(f"Hue range: [{min_hue} .. {max_hue}]")
        log.info(f"Hue calibrated: {avg_hue}")

        success = True
        return avg_hue, success

    else:
        log.warning(f"Hue calibration failed.")

        hue = 22  # Reasonable default
        success = False
        return hue, success


def calibrate_pos(camera_fn, detector_fn):
    for i in range(20):  # Try and detect for 20 frames before giving up
        img_frame, elapsed_time = camera_fn()
        ball_detected, ((x, y), radius) = detector_fn(img_frame)

        # If we found a ball roughly in the center that is large enough
        if ball_detected and ball_close_enough(x, y, radius):
            success = True

            x_offset = round(x, 3)
            y_offset = round(y, 3)

            log.info(f"Offset calibrated: [{x_offset:.3f}, {y_offset:.3f}]")
            return (x_offset, y_offset), success

    log.warning(f"Offset calibration failed.")
    success = False
    return (0.0, 0.0), success


def calibrate_servo_offsets(pid_fn, env, stationary_vel=0.01, time_limit=20):
    start_time = time.time()
    action = Vector2(0, 0)

    # Initial high vel_history (to use the vel_hist[-10:] later)
    vel_x_hist = [1.0 for _ in range(10)]
    vel_y_hist = [1.0 for _ in range(10)]

    # Run until the ball has stabilized or the time limit was reached
    while time.time() < start_time + time_limit:
        state = env.step(action)
        action, info = pid_fn(state)

        ball_detected, (x, y, vel_x, vel_y, sum_x, sum_y) = state
        if ball_detected:
            vel_x_hist.append(vel_x)
            vel_y_hist.append(vel_y)
            prev_10_x = np.mean(vel_x_hist[-10:])
            prev_10_y = np.mean(vel_y_hist[-10:])

            # If the average velocity for the last 10 timesteps is under the limit
            if (prev_10_x < stationary_vel) and (prev_10_y < stationary_vel):
                success = True

                # Calculate offsets by calculating servo positions at the
                # current stable position and subtracting the `default` zeroed
                # position of the servos.
                servos = np.array(plate_angles_to_servo_positions(*action))
                servos_zeroed = np.array(plate_angles_to_servo_positions(0, 0))
                servos_offsets = list(servos - servos_zeroed)

                return servos_offsets, success

    # If the plate could be stabilized in time_limit seconds, quit
    log.warning(f"Servo calibration failed.")
    success = False
    return [0.0, 0.0, 0.0], success


def write_calibration(calibration_dict, calibration_file="calibration.json"):
    log.info("Writing calibration.")

    # write out stuff
    with open(calibration_file, "w+") as outfile:
        log.info(f"Creating calibration file {calibration_file}")
        json.dump(calibration_dict, outfile, indent=4, sort_keys=True)


def run_calibration(env, pid_fn):
    # Get some hidden things from env
    hat = env.hat
    camera_fn = env.camera
    detector_fn = env.detector

    # TODO: debug this, there was a regression in firmware
    # # Wait until the user presses the joystick
    # while True:
    #     hat.noop()
    #     menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
    #     time.sleep(1 / 30)
    #     print(f"menu_btn:{menu_btn}, joy_btn:{joy_btn}, joy_x:{joy_x}, joy_y:{joy_y}")
    #     if joy_btn:
    #         break

    hat.print_info_screen()

    (x_offset, y_offset), success_pos = calibrate_pos(camera_fn, detector_fn)
    print(f"offsets: (x={x_offset}, y={y_offset}), success={success_pos}.")
    input("Press enter...")

    # TODO: you can trigger a massive fw freakout by calling this (so don't):
    # hat.set_icon_text(Icon.X, Text.CAL_INSTR)

    hue, success_hue = calibrate_hue(camera_fn, detector_fn)
    print(f"(hue={hue}, success_hue={success_hue}.")
    input("Press enter...")

    hat.print_arbitrary_string(
        "Remove the\n"
        "ball stand and\n"
        "place the ball\n"
        "in the middle.\n"
        "Then press the\n"
        "Joystick button.\n"
    )

    # TODO: major bug: for some reason, print_arbitrary_string *breaks ability to read the
    # joysticks which is why temporarily we have "input"

    servos_offsets, success_offsets = calibrate_servo_offsets(pid_fn, env)
    print(f"(offsets={servos_offsets}, success={success_offsets}.")

    if success_hue and success_pos and success_offsets:
        # If all succeeded
        hat.set_icon_text(Icon.CHECK, Text.CAL_COMPLETE)
    elif success_hue or success_pos or success_offsets:
        # If only some succeeded
        success_hue_str = "succeeded" if success_hue else "failed"
        success_pos_str = "succeeded" if success_pos else "failed"
        success_offsets_str = "succeeded" if success_offsets else "failed"
        hat.print_arbitrary_string(
            f"Calibrate hue {success_hue_str}\n"
            f"Calibrate position {success_pos_str}\n"
            f"Calibrate offsets {success_offsets_str}\n"
        )
    else:
        # If none succeeded
        hat.set_icon_text(Icon.X, Text.CAL_FAILED)
        return  # Exit immediately

    calibration_dict = {
        "ball_hue": hue,
        "plate_x_offset": x_offset,
        "plate_y_offset": y_offset,
        "rotation": -30.0,
        "servo_offsets": servos_offsets,
    }

    write_calibration(calibration_dict)


# def main(frequency=30, debug=True):
#     pid_fn = pid_controller(frequency=frequency)

#     with MoabEnv(frequency=frequency, debug=debug) as env:
#         state = env.reset(Icon.DOT, Text.CAL_INSTR)
#         run_calibration(env, pid_fn)


def main(frequency=30, debug=True):
    pid_fn = pid_controller(frequency=frequency)

    with MoabEnv(frequency=frequency, debug=debug) as env:
        state = env.reset(Icon.DOT, Text.BLANK)
        run_calibration(env, pid_fn)


if __name__ == "__main__":
    main()
