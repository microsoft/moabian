# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
HSV filtering ball detector
"""

import cv2
import math
import numpy as np
from hsv import hue_to_bgr
from huemask import hue_mask
from common import Vector2, CircleFeature, Calibration

from typing import List, Optional


def pixels_to_meters(vec, frame_size=256, field_of_view=1.05):
    # The plate is default roughly 105% of the field of view
    plate_diameter_meters = 0.225
    plate_diameter_pixels = frame_size * field_of_view
    conversion = plate_diameter_meters / plate_diameter_pixels
    return np.asarray(vec) * conversion


def meters_to_pixels(vec, frame_size=256, field_of_view=1.05):
    # The plate is default roughly 105% of the field of view
    plate_diameter_meters = 0.225
    plate_diameter_pixels = frame_size * field_of_view
    conversion = plate_diameter_meters / plate_diameter_pixels
    return np.int_(np.asarray(vec) / conversion)  # Note: pixels are only ever ints


def draw_ball(img, center, radius, hue):
    bgr = hue_to_bgr(hue)
    cv2.circle(img, center, 2, bgr, 2)
    cv2.circle(img, center, int(radius), bgr, 2)
    return img


def save_img(filepath, img, rotated=False, quality=80):
    if rotated:
        # Rotate the image -30 degrees so it looks normal
        w, h = img.shape[:2]
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, 30, 1.0)
        img = cv2.warpAffine(img, M, (w, h))
        img = img[::-1, :, :]  # Mirror along x axis

    cv2.imwrite(
        filepath,
        img,
        [cv2.IMWRITE_JPEG_QUALITY, quality],
    )


def hsv_detector(
    calibration=None,
    frame_size=256,
    kernel_size=[5, 5],
    ball_min=0.06,
    ball_max=0.22,
    hue=None,  # hue [0..255]
    sigma=0.05,  # narrow: 0.01, wide: 0.1
    bandpass_gain=12.0,
    mask_gain=4.0,
    debug=False,
):
    if calibration is None:
        calibration = Calibration()
    # if we haven't been overridden, use ballHue from calibration
    if hue is None:
        hue = calibration.ball_hue
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, tuple(kernel_size))

    def detect_features(img, hue=hue, debug=debug, filename="/tmp/camera/frame.jpg"):
        # covert to HSV space
        color = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # The hue_mask function follows CV2 convention and hue is in the range
        # [0, 180] instead of [0, 360]
        hue /= 2

        # run through each triplet and perform our masking filter on it.
        # hue_mask coverts the hsv image into a grayscale image with a
        # bandpass applied centered around hue, with width sigma
        hue_mask(color, hue, sigma, bandpass_gain, mask_gain)

        # convert to b&w mask from grayscale image
        mask = cv2.inRange(color, np.array((200, 200, 200)), np.array((255, 255, 255)))

        # expand b&w image with a dialation filter
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )[-2]

        if len(contours) > 0:
            contour_peak = max(contours, key=cv2.contourArea)
            ((x_obs, y_obs), radius) = cv2.minEnclosingCircle(contour_peak)

            # Determine if ball size is the appropriate size
            norm_radius = radius / frame_size
            if ball_min < norm_radius < ball_max:
                ball_detected = True

                # Convert from pixels to absolute with 0,0 as center of detected plate
                x = x_obs - frame_size // 2
                y = y_obs - frame_size // 2

                if debug:
                    ball_center_pixels = (int(x_obs), int(y_obs))
                    # TODO: scott validate this hue will work if [0,180] or [0,360]
                    draw_ball(img, ball_center_pixels, radius, hue)
                    save_img(filename, img, rotated=False, quality=80)

                # Rotate the x, y coordinates by -30 degrees
                center = Vector2(x, y).rotate(np.radians(-30))
                center = pixels_to_meters(center, frame_size)
                return ball_detected, (center, radius)

        # If there were no contours or no contours the size of the ball
        ball_detected = False
        if debug:
            save_img(filename, img, rotated=False, quality=80)
        return ball_detected, (Vector2(0, 0), 0.0)

    return detect_features
