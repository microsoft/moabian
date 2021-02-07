# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
A sensor that uses OpenCV for capture
"""

import numpy as np
import threading
import cv2

from time import time


# Link to raspicam_cv implementation for mapping values
# https://github.com/cedricve/raspicam/blob/651c56418a5a594fc12f1414eb14f2b899729cb1/src/raspicam_cv.h#L108
class OpenCVCameraSensor:
    def __init__(
        self,
        device_id=0,
        rotation=0,
        brightness=60,
        contrast=0,
        fps=30,
    ):
        self.device_id = device_id
        # self.width = width
        # self.height = height
        self.rotation = rotation
        self.brightness = brightness
        self.contrast = contrast
        self.fps = fps
        self.prev_time = 0.0
        self.source = None
        self.last_frame = None

    def start(self):
        self.source = cv2.VideoCapture(self.device_id)
        if self.source:
            self.source.set(cv2.CAP_PROP_FRAME_WIDTH, 384)
            self.source.set(cv2.CAP_PROP_FRAME_HEIGHT, 288)
            self.source.set(cv2.CAP_PROP_FPS, self.fps - 5)
            self.source.set(cv2.CAP_PROP_MODE, 0)  # Not meant to be configurable
            self.source.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            self.source.set(cv2.CAP_PROP_CONTRAST, self.contrast)
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
            frame = frame[:-24, 40:-80]  # Crop so middle of plate is middle of image
            cv2.resize(frame, (256, 256))  # Crop off edges to make image (256, 256)
            return frame, elapsed_time
        else:
            raise ValueError("Could not get the next frame")
