# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Calibration Controller

Performs calibration for hue, center of camera position, and servo offsets
"""

import os
import cv2
import time
import json
import argparse
import datetime
import numpy as np
import logging as log

from env import MoabEnv
from common import Vector2
from detector import hsv_detector
from controllers import pid_controller
from hat import Hat, plate_angles_to_servo_positions


def ball_close_enough(x, y, radius, max_ball_dist=0.045, min_ball_dist=0.01):
    # reject balls which are too far from the center and too small
    return (
        np.abs(x) < max_ball_dist
        and np.abs(y) < max_ball_dist
        and radius > min_ball_dist
    )


def calibrate_hue(camera_fn, detector_fn, hue_low=0, hue_high=360, hue_steps=41):
    img_frame, elapsed_time = camera_fn()
    hue_options = list(np.linspace(hue_low, hue_high, hue_steps))

    detected_hues = []
    for hue in hue_options:
        img_frame, elapsed_time = camera_fn()
        ball_detected, ((x, y), radius) = detector_fn(img_frame, hue=hue)

        # If we found a ball roughly in the center that is large enough
        if ball_detected and ball_close_enough(x, y, radius):
            print(
                f"hue={hue:0.3f}, ball_detected={ball_detected}, "
                f"(x, y)={x:0.3f} {y:0.3f}, radius={radius:0.3f}"
            )
            detected_hues.append(hue)

    if len(detected_hues) > 0:
        # https://en.wikipedia.org/wiki/Mean_of_circular_quantities
        detected_hues_rad = np.radians(detected_hues)
        sines, cosines = np.sin(detected_hues_rad), np.cos(detected_hues_rad)
        sin_mean, cos_mean = np.mean(sines), np.mean(cosines)
        avg_hue_rad = np.arctan2(sin_mean, cos_mean)
        avg_hue = np.degrees(avg_hue_rad) % 360  # Convert back to [0, 360]

        print(f"Hues are: {detected_hues}")
        print(f"Hue calibrated: {avg_hue:0.3f}")

        success = True
        return avg_hue, success

    else:
        log.warning(f"Hue calibration failed.")

        hue = 44  # Reasonable default
        success = False
        return hue, success


def calibrate_pos(camera_fn, detector_fn, hue):
    for i in range(10):  # Try and detect for 10 frames before giving up
        img_frame, elapsed_time = camera_fn()
        ball_detected, ((x, y), radius) = detector_fn(img_frame, hue=hue)

        # If we found a ball roughly in the center that is large enough
        if ball_detected and ball_close_enough(x, y, radius):
            success = True

            x_offset = round(x, 3)
            y_offset = round(y, 3)

            log.info(f"Offset calibrated: [{x_offset:.3f}, {y_offset:.3f}]")
            print(f"Offset calibrated: [{x_offset:.3f}, {y_offset:.3f}]")
            return (x_offset, y_offset), success

    log.warning(f"Offset calibration failed.")
    success = False
    return (0.0, 0.0), success


# TODO: optimize this calibration
def calibrate_servo_offsets(pid_fn, env, stationary_vel=0.001, time_limit=20):
    start_time = time.time()
    action = Vector2(0, 0)

    # Initial high vel_history (to use the vel_hist[-100:] later)
    vel_x_hist = [1.0 for _ in range(100)]
    vel_y_hist = [1.0 for _ in range(100)]

    # Run until the ball has stabilized or the time limit was reached
    while time.time() < start_time + time_limit:
        state = env.step(action)
        action, info = pid_fn(state)

        (x, y, vel_x, vel_y, sum_x, sum_y), ball_detected, buttons = state
        if ball_detected:
            vel_x_hist.append(vel_x)
            vel_y_hist.append(vel_y)
            prev_100_x = np.mean(vel_x_hist[-100:])
            prev_100_y = np.mean(vel_y_hist[-100:])

            # If the average velocity for the last 100 timesteps is under the limit
            if (prev_100_x < stationary_vel) and (prev_100_y < stationary_vel):
                success = True

                # Calculate offsets by calculating servo positions at the
                # current stable position and subtracting the `default` zeroed
                # position of the servos.
                servos = np.array(plate_angles_to_servo_positions(*action))
                servos_zeroed = np.array(plate_angles_to_servo_positions(0, 0))
                servo_offsets = list(servos - servos_zeroed)

                return servo_offsets, success

    # If the plate could be stabilized in time_limit seconds, quit
    log.warning(f"Servo calibration failed.")
    success = False
    return [0.0, 0.0, 0.0], success


def write_calibration(calibration_dict, calibration_file="bot.json"):
    log.info("Writing calibration.")

    # write out stuff
    with open(calibration_file, "w+") as outfile:
        log.info(f"Creating calibration file {calibration_file}")
        json.dump(calibration_dict, outfile, indent=4, sort_keys=True)


def read_calibration(calibration_file="bot.json"):
    log.info("Reading previous calibration.")

    if os.path.isfile(calibration_file):
        with open(calibration_file, "r") as f:
            calibration_dict = json.load(f)
    else:  # Use defaults
        calibration_dict = {
            "ball_hue": 44,
            "plate_x_offset": 0.0,
            "plate_y_offset": 0.0,
            "servo_offsets": [0.0, 0.0, 0.0],
        }
    return calibration_dict


def wait_for_joystick(hat, sleep_time=1 / 30):
    while True:
        hat.noop()  # Force new transfer to have up to date button reading
        menu_btn, joy_btn, joy_x, joy_y = hat.get_buttons()
        time.sleep(sleep_time)
        if joy_btn:
            return


def wait_for_menu(hat, sleep_time=1 / 30):
    while True:
        hat.noop()  # Force new transfer to have up to date button reading
        menu_btn, joy_btn, joy_x, joy_y = hat.get_buttons()
        time.sleep(sleep_time)
        if menu_btn:
            return


def run_calibration(env, pid_fn, calibration_file):
    # Get some hidden things from env
    hat = env.hat
    camera_fn = env.camera
    detector_fn = env.detector

    success_pos = True
    success_hue = True
    success_offsets = True

    # lift plate up fist
    hat.set_angles(0, 0)

    # Calibrate position and hue
    hat.display_long_string(
        "To calibrate:\n\n"
        "Place ball in\ncenter using\nclear stand.\n\n"
        "Then click joystick\nto continue.\n"
    )
    wait_for_joystick(hat)
    hat.display_string("Calibrating...")
    hue, success_hue = calibrate_hue(camera_fn, detector_fn)
    (x_offset, y_offset), success_pos = calibrate_pos(camera_fn, detector_fn, hue)

    # # Calibrate servo offsets
    # hat.display_long_string(
    #     "Calibarating\noffsets\n\n"
    #     "Place ball in\ncenter using\nclear stand.\n\n"
    #     "Click joystick\nto continue."
    # )
    # wait_for_joystick(hat)
    # hat.display_long_string("Running auto-\ncalibrate servos...")
    # servo_offsets, success_offsets = calibrate_servo_offsets(pid_fn, env)

    # Save calibration
    calibration_dict = read_calibration(calibration_file)
    calibration_dict["ball_hue"] = hue
    calibration_dict["plate_x_offset"] = x_offset
    calibration_dict["plate_y_offset"] = y_offset
    # calibration_dict["servo_offsets"] = servo_offsets
    # o1, o2, o3 = servo_offsets
    write_calibration(calibration_dict)

    # Update the environment to use the new calibration
    # Warning! This mutates the state!
    env.reset_calibration(calibration_file=calibration_file)

    if success_pos and success_hue:  # and success_offsets:
        hat.display_long_string(
            "Calibration\nsuccessful\n\n"
            f"Ball hue = {hue:.1f}\n\n"
            f"Position = \n({100*x_offset:.1f}, {100*y_offset:.1f}) cm\n\n"
            # f"servo offsets = ({o1:.2f}, {o2:.2f}, {o3:.2f})\n\n"
            "Click menu\nto return...\n"
        )
    elif not (success_pos or success_hue):  # or success_offsets):
        hat.display_long_string("Calibration\nfailed\n\nClick menu\nto return...")
    else:
        hue_str = (
            f"Hue calib:\nsuccessful\nBall hue = {hue:.1f}\n\n"
            if success_hue
            else "Hue calib:\nfailed\n\n"
        )
        pos_str = (
            f"Position \ncalib:\nsuccessful\nPosition = \n({100*x_offset:.1f}, {100*y_offset:.1f})cm\n\n"
            if success_hue
            else "(X, Y) calib:\nfailed\n\n"
        )
        hat.display_long_string(
            "Calibration\npartially succeeded\n\n"
            + hue_str
            + pos_str
            + "Click menu\nto return...\n"
        )

    hat.hover()

    # When the calibration is complete, write the image of what the moab camera
    # sees (useful for debugging when the hue calibration fails)
    # Have a nice filename with the time and whether it succeeded or failed
    time_of_day = datetime.datetime.now().strftime("%H%M%S")
    filename = f"/tmp/hue.{time_of_day}."
    filename += "success" if success_hue else "fail"
    filename += ".jpg"
    img_frame, _ = camera_fn()
    detector_fn(img_frame, debug=True, filename=filename)

    return None, {}


def main(calibration_file, frequency=30, debug=True):
    pid_fn = pid_controller(frequency=frequency)

    with MoabEnv(frequency=frequency, debug=debug) as env:
        env.step((0, 0))
        time.sleep(0.2)
        run_calibration(env, pid_fn, calibration_file)
        wait_for_menu(env.hat)


if __name__ == "__main__":  # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-f", "--file", default="bot.json", type=str)

    args, _ = parser.parse_known_args()
    main(args.file, debug=args.debug)
