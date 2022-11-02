# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
A sensor that uses OpenCV for capture
"""

import cv2
import threading
import numpy as np

from time import time


# Link to raspicam_cv implementation for mapping values
# https://github.com/cedricve/raspicam/blob/651c56418a5a594fc12f1414eb14f2b899729cb1/src/raspicam_cv.h#L108
class OpenCVCameraSensor:
    def __init__(
        self,
        device_id=0,
        rotation=0,
        brightness=60,
        contrast=100,
        frequency=30,
        x_offset_pixels=0,
        y_offset_pixels=0,
        auto_exposure=True,
        exposure=50,  # int for manual (each 1 is 100µs of exposure)
    ):
        self.device_id = device_id
        # self.width = width
        # self.height = height
        self.rotation = rotation
        self.brightness = brightness
        self.contrast = contrast
        self.frequency = frequency
        self.auto_exposure = auto_exposure
        self.exposure = exposure
        self.prev_time = 0.0
        self.source = None
        self.last_frame = None
        self.x_offset_pixels = x_offset_pixels
        self.y_offset_pixels = y_offset_pixels

    def start(self):
        self.source = cv2.VideoCapture(self.device_id)
        if self.source:
            self.source.set(cv2.CAP_PROP_FRAME_WIDTH, 384)
            self.source.set(cv2.CAP_PROP_FRAME_HEIGHT, 288)
            self.source.set(cv2.CAP_PROP_FPS, self.frequency)
            self.source.set(cv2.CAP_PROP_MODE, 0)  # Not meant to be configurable
            self.source.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            self.source.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.source.set(
                cv2.CAP_PROP_AUTO_EXPOSURE, 0.25 if self.auto_exposure else 0.75
            )
            self.source.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        else:
            raise Exception("Couldn't create camera.")

    def stop(self):
        if self.source:
            self.source.release()
            self.source = None

    def __call__(self):
        # safety check
        if self.source is None:
            raise Exception("Using camera before it has been started.")

        # Calculate the time elapsed since the last sensor snapshot
        curr_time = time()
        elapsed_time = curr_time - self.prev_time
        self.prev_time = curr_time

        ret, frame = self.source.read()
        if ret:
            w, h = 384, 288
            d = 256  # Our final "destination" rectangle is 256x256

            # Ensure the offset crops are possible
            x_offset_pixels = min(self.x_offset_pixels, (w / 2 - d / 2))
            x_offset_pixels = max(self.x_offset_pixels, -(w / 2 - d / 2))
            y_offset_pixels = min(self.y_offset_pixels, (h / 2 - d / 2))
            y_offset_pixels = max(self.y_offset_pixels, -(h / 2 - d / 2))

            # Calculate the starting point in x & y
            x = int((w / 2 - d / 2) + x_offset_pixels)
            y = int((h / 2 - d / 2) + y_offset_pixels)

            frame = frame[y : y + d, x : x + d]
            # frame = frame[:-24, 40:-80]  # Crop so middle of plate is middle of image
            # cv2.resize(frame, (256, 256))  # Crop off edges to make image (256, 256)
            return frame, elapsed_time
        else:
            raise ValueError("Could not get the next frame")
