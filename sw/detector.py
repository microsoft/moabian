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
from typing import List, Optional
from common import Vector2, CircleFeature


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


def draw_ball(img, center, radius, hue):
    bgr = hue_to_bgr(hue)
    # 45 -> hsl(45°, 75%, 50%)
    cv2.circle(img, center, 2, bgr, 2)
    cv2.circle(img, center, int(radius), bgr, 2)
    return img


def draw_crosshairs(img, crosshairs):
    x, y = crosshairs
    ly, lx = img.shape[:2]  # Note: y, x
    cv2.line(img, (0, ly // 2 + y), (lx, ly // 2 + y), (0, 0, 255), 2)  # X axis
    cv2.line(img, (lx // 2 + x, 0), (lx // 2 + x, ly), (0, 0, 255), 2)  # Y axis
    return img


def save_img(filepath, img, rotated=False, quality=80, mirrored=False):
    if rotated:
        # Rotate the image -30 degrees so it looks normal
        w, h = img.shape[:2]
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, 30, 1.0)
        img = cv2.warpAffine(img, M, (w, h))
        img = img[::-1, :, :]  # Mirror along x axis

    # Only mirror if the image is not rotated (which does the flip already)
    elif mirrored:
        img = img[::-1, :, :]  # Mirror along x axis

    cv2.imwrite(
        filepath,
        img,
        [cv2.IMWRITE_JPEG_QUALITY, quality],
    )


def hsv_detector(
    frame_size=256,
    kernel_size=[5, 5],
    ball_min=0.06,
    ball_max=0.22,
    hue=44,  # hue [0..360]
    debug=False,
):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, tuple(kernel_size))

    def detect_features(
        img,
        hue=hue,
        pixel_offsets=(0, 0),
        debug=debug,
        filename="/tmp/camera/frame.jpg",
        crosshairs=None,
        axis=False,
    ):
        # covert to HSV space
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # The hue_mask function follows CV2 convention and hue is in the range
        # [0, 180] instead of [0, 360]
        # run through each triplet and perform our masking filter on it.
        # hue_mask coverts the hsv image into a grayscale image with a
        # bandpass applied centered around hue, with width sigma
        hue_mask(img_hsv, hue / 2, 0.03, 60.0, 1.5)

        # convert to b&w mask from grayscale image
        mask = cv2.inRange(
            img_hsv, np.array((200, 200, 200)), np.array((255, 255, 255))
        )

        # expand b&w image with a dialation filter
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )[-2]

        # Determine the zero point in the image
        center_x = img.shape[1] // 2 + pixel_offsets[0]  # img.shape[1] is width (x)
        center_y = img.shape[0] // 2 + pixel_offsets[1]  # img.shape[0] is height (y)

        if len(contours) > 0:
            contour_peak = max(contours, key=cv2.contourArea)
            ((x_obs, y_obs), radius) = cv2.minEnclosingCircle(contour_peak)

            # Determine if ball size is the appropriate size
            norm_radius = radius / frame_size
            if ball_min < norm_radius < ball_max:
                ball_detected = True

                # Convert from pixels to absolute with 0,0 as center of detected plate
                x = x_obs - center_x
                y = y_obs - center_y

                if debug:
                    ball_center_pixels = (int(x_obs), int(y_obs))
                    draw_ball(img, ball_center_pixels, radius, hue)
                    if crosshairs is not None:
                        draw_crosshairs(img, crosshairs)
                    if axis:
                        draw_crosshairs(img, (pixel_offsets[0], pixel_offsets[1]))
                    save_img(filename, img, rotated=False, quality=80, mirrored=False)

                # Rotate the x, y coordinates by -30 degrees
                x, y = pixels_to_meters((x, y))
                center = Vector2(x, y).rotate_deg(-30)

                return ball_detected, (center, radius)

        # If there were no contours or no contours the size of the ball
        ball_detected = False
        if debug:
            if crosshairs is not None:
                draw_crosshairs(img, crosshairs)
            if axis:
                draw_crosshairs(img, (pixel_offsets[0], pixel_offsets[1]))
            save_img(filename, img, rotated=False, quality=80, mirrored=False)
        return ball_detected, (Vector2(0, 0), 0.0)

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