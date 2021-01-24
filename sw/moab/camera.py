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
        width=256,
        height=256,
        rotation=0,
        brightness=50,
        contrast=100,
        saturation=100,
        gain=100,
        fps=30,
    ):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.rotation = rotation
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.gain = gain
        self.fps = fps
        self.prev_time = 0.0
        self.source = None
        self.last_frame = None

    def start(self):
        self.source = cv2.VideoCapture(self.device_id)
        if self.source:
            cv2.CAP_PROP_FRAME_WIDTH = self.width
            cv2.CAP_PROP_FRAME_HEIGHT = self.height
            cv2.CAP_PROP_FPS = self.fps
            cv2.CAP_PROP_BRIGHTNESS = self.brightness
            cv2.CAP_PROP_CONTRAST = self.contrast
            cv2.CAP_PROP_CONTRAST = self.saturation
            cv2.CAP_PROP_CONTRAST = self.gain
            # Not meant to be configurable
            cv2.CAP_PROP_MODE = 0
        else:
            raise Exception("Couldn't create camera.")

    def stop(self):
        if self.source:
            self.source.release()
            self.source = None

    def __call__(self, save=False):
        # safety check
        if self.source is None:
            raise Exception("Using camera before it has been started.")

        # Calculate the time elapsed since the last sensor snapshot
        curr_time = time()
        elapsed_time = curr_time - self.prev_time
        self.prev_time = curr_time

        ret, frame = self.source.read()
        if ret:
            if save:
                cv2.imwrite("/tmp/frame.jpg", frame, 70)
            return frame, elapsed_time
        else:
            raise ValueError("Could not get the next frame")
