# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import cv2
import time
import json
import math
import argparse
import numpy as np

from hat import Hat, Icon
from common import Vector2
from huemask import hue_mask
from env import MoabEnv, EnvState
from typing import Tuple, List, Optional
from dataclasses import dataclass, astuple
from detector import pixels_to_meters, draw_ball, save_img
from controllers import pid_controller, pid_circle_controller, joystick_controller


def old_hsv_detector(
    frame_size=256,
    kernel_size=[5, 5],
    ball_min=0.06,
    ball_max=0.22,
    debug=False,
):
    hue = 60  # Orange as default
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, tuple(kernel_size))

    def detect_features(img, hue=hue, debug=debug, filename="/tmp/camera/frame.jpg"):
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hue_mask(img_hsv, hue / 2, 0.05, 12.0, 4.0)
        mask = cv2.inRange(img_hsv, np.array([200] * 3), np.array([255] * 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[-2]

        if len(contours) > 0:
            contour_peak = max(contours, key=cv2.contourArea)
            ((x_obs, y_obs), radius) = cv2.minEnclosingCircle(contour_peak)

            norm_radius = radius / frame_size
            if ball_min < norm_radius < ball_max:
                ball_detected = True
                x = x_obs - frame_size // 2
                y = y_obs - frame_size // 2

                if debug:
                    ball_center_pixels = (int(x_obs), int(y_obs))
                    draw_ball(img, ball_center_pixels, radius, hue)
                    save_img(filename, img, rotated=False, quality=80)

                center = Vector2(x, y).rotate(np.radians(-30))
                center = pixels_to_meters(center, frame_size)
                return ball_detected, (center, radius)

        ball_detected = False
        if debug:
            save_img(filename, img, rotated=False, quality=80)
        return ball_detected, (Vector2(0, 0), 0.0)

    return detect_features


class MoabDatasetEnv(MoabEnv):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.detector = old_hsv_detector(debug=True)  # Use the old detector for now

    def step(self, action, hue=70):
        plate_x, plate_y = action
        self.hat.set_angles(plate_x, plate_y)
        frame, elapsed_time = self.camera()
        img_copy = np.copy(frame)
        ball_detected, cicle_feature = self.detector(frame, hue=hue)
        ball_center, ball_radius = cicle_feature
        x, y = ball_center
        vel_x, vel_y = self.vel_x(x), self.vel_y(y)
        self.sum_x += x
        self.sum_y += y
        buttons = self.hat.get_buttons()
        state = EnvState(x, y, vel_x, vel_y, self.sum_x, self.sum_y)
        return state, ball_detected, buttons, img_copy


def main(controller, filepath="/tmp/dataset/"):
    def wait(env):
        sleep_time = 1 / env.frequency
        while True:
            env.hat.noop()  # Force new transfer to have up to date button reading
            buttons = env.hat.get_buttons()
            if buttons.menu_button:
                return buttons
            time.sleep(sleep_time)

    ball_colors = [
        ("orange", 60),
        ("yellow", 80),
        ("green", 130),
        ("blue", 200),
        ("pink", 320),
        ("purple", 270),  # This doesn't work anyway...
        ("no ball", 0),
    ]
    print("For every ball color, click menu to display color to place in the")
    print("center then click to start the dataset generation for each ball. After")
    print("it's finished, screen will display a new ball color to try.\n")
    counter_interval = 5

    # Create folder to save images
    if not os.path.isdir(filepath):
        os.makedirs(filepath)

    with MoabDatasetEnv(frequency=30, debug=True) as env:
        env.hat.enable_servos()
        env.hat.display_string_icon("", Icon.PAUSE)

        for (color, hue) in ball_colors:
            print("Running:", color)
            env.hat.display_string_icon(color, Icon.PAUSE)
            wait(env)  # Wait until menu is clicked
            state, detected, buttons, img = env.reset(text="RUNNING", icon=Icon.DOT)

            start_time = time.time()
            counter = 0
            while time.time() - start_time < 5:  # Run for ~5 seconds
                action, info = controller((state, detected, buttons))
                state, detected, buttons, img = env.step(action)

                if counter % counter_interval == 0:
                    i = counter // counter_interval
                    if detected:
                        filename = f"{color}.{i}.jpg"
                    else:
                        filename = f"undetected.{color}.{i}.jpg"
                    
                    print(filename)
                    save_img(filepath + filename, img, quality=80)

                counter += 1


if __name__ == "__main__":
    CONTROLLERS = {
        "pid": pid_controller,
        "pid-circle": pid_circle_controller,
        "joystick": joystick_controller,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--controller",
        default="joystick",
        choices=list(CONTROLLERS.keys()),
        help=f"""Select what type of action to take.
        Options are: {CONTROLLERS.keys()}
        """,
    )
    parser.add_argument(
        "-p",
        "--path",
        default="/tmp/dataset/",
        type=str,
        help="""The directory to save the dataset (required trailing /).
        Could be something like ~/dataset/bright-daylight/
        """,
    )
    args, _ = parser.parse_known_args()
    controller = CONTROLLERS[args.controller]()
    main(controller, filepath=args.path)
