# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
HSV filtering ball detector
"""

import cv2
import time
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


def pixel_to_meter_ratio(frame_size=256, field_of_view=1.05):
    # The plate is default roughly 105% of the field of view
    plate_diameter_meters = 0.225
    plate_diameter_pixels = frame_size * field_of_view
    conversion = plate_diameter_meters / plate_diameter_pixels
    return conversion


def draw_ball(img, center, radius, color):
    cv2.circle(img, center, 2, color, 2)
    cv2.circle(img, center, int(radius), color, 2)
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
    hue=None,
    debug=False,
):
    dp = 1
    min_dist = 10
    param1 = 300
    param2 = 30
    ball_min = 0.06  # Fraction of the image size
    ball_max = 0.22  # Fraction of the image size
    min_radius = int(ball_min * frame_size)
    max_radius = int(ball_max * frame_size)

    def detect_features(img, hue=None, debug=debug, filename="/tmp/camera/frame.jpg"):
        img = cv2.medianBlur(img, 5)
        gray_img = cv2.cvtColor(img[:,:,::-1], cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            gray_img,
            cv2.HOUGH_GRADIENT,
            dp,
            minDist=min_dist,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius
        )

        if circles is not None and circles.shape[1] > 0:
            circles = np.uint(np.around(circles))
            circles = circles[0]
            # Consider the first circle to be the correct one
            ball_detected = True
            main_x, main_y, main_radius = circles[0]

            if debug:
                # Draw additional circles if necessary (useful for debugging)
                if circles.shape[0] > 1:
                    for x, y, radius in circles[1:]:
                        # Draw the less important ones
                        draw_ball(img, (x, y), radius, (255, 100, 100))

                # Putting this last makes sure to draw this circle on top
                draw_ball(img, (main_x, main_y), main_radius, (255, 0, 0))
                
                save_img(filename, img, rotated=False, quality=80)

            # Rescale to [-frame_size/2, +frame_size/2], rotate, then convert to meters
            main_x -= frame_size // 2
            main_y -= frame_size // 2
            center = Vector2(main_x, main_y).rotate(np.radians(-30))
            center = pixels_to_meters(center, frame_size)
            radius = main_radius

        else:
            # If there were no contours or no contours the size of the ball
            ball_detected = False
            if debug:
                save_img(filename, img, rotated=False, quality=80)
            center = Vector2(0, 0)
            radius = 0.0

        return ball_detected, (center, radius)

    return detect_features


def circle_test_detector(hue=44, debug=False, *args, **kwargs):
    angle = 0
    time = 1
    frequency = 30  # in Hz
    scale = pixel_to_meter_ratio()
    radius = 256 * 0.4
    ball_radius_pixels = 256 * 0.1

    def detect_features(img, hue=hue, debug=debug, filename="/tmp/camera/frame.jpg"):
        nonlocal angle
        angle += (1 / (time * frequency)) * (2 * np.pi)
        x_pixels, y_pixels = (radius * np.sin(angle), radius * np.cos(angle))
        x_pixels += 256 / 2
        y_pixels += 256 / 2

        if debug:
            ball_center_pixels = (int(x_pixels), int(y_pixels))
            print(ball_center_pixels)
            draw_ball(img, ball_center_pixels, ball_radius_pixels, hue)
            save_img(filename, img, rotated=False, quality=80)

        x, y = x_pixels * scale, y_pixels * scale
        ball_detected = True
        return ball_detected, (Vector2(x, y), ball_radius_pixels * scale)

    return detect_features
