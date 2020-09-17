# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
A sensor that use PiCamera for capture.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from time import time
from threading import Event
from picamera import PiCamera
from typing import Optional, Tuple
from picamera.array import PiRGBArray

from ..common import ISensor, IDevice


class PiCameraSensor(ISensor):
    @dataclass
    class Config(ISensor.Config):
        framerate: int = 30
        exposureMode: str = "off"

        brightness: int = 70
        contrast: int = 25
        rotated: bool = True

        ballOffsetX: int = 0
        ballOffsetY: int = 0

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config

        self.camera = PiCamera()

        self.camera.resolution = [self.config.width, self.config.height]
        self.camera.framerate = self.config.framerate

        self.camera.exposure_mode = self.config.exposureMode
        self.camera.brightness = self.config.brightness
        self.camera.contrast = self.config.contrast

        self.frame_raw = None

        self.x_offset_left = 0
        self.x_offset_right = 0
        self.y_offset_bottom = 0
        self.y_offset_top = 0

        self.prevTime = 0.0

    def getNextInput(self, sender: IDevice) -> Tuple[float, Optional[np.ndarray]]:

        # Calculate the time elapsed since the last sensor snapshot
        currTime = time()
        elapsedTime = currTime - self.prevTime
        self.prevTime = currTime

        f = self.stream.__next__()
        self.frame_raw = f.array
        self.rawCapture.truncate(0)

        if self.frame_raw is not None:
            frame = self.frame_raw[
                self.x_offset_right : (self.config.width - self.x_offset_left),
                self.y_offset_bottom : (self.config.height - self.y_offset_top),
            ]
            if self.config.rotated:
                frame = self._rotate_image(frame, self.image_size)

            frame = cv2.flip(frame, 0)

            return (elapsedTime, frame)
        else:
            return (elapsedTime, None)

    def start(self):
        self._init_camera()
        self.kill = Event()

    def stop(self):
        self.stream.close()
        self.rawCapture.close()

    def _center_camera(self, ball_x, ball_y):
        if ball_x < 0:
            self.x_offset_right = abs(ball_x * 2)

        elif ball_x > 0:
            self.x_offset_left = abs(ball_x * 2)

        else:
            self.x_offset_left = 0
            self.x_offset_right = 0

        if ball_y < 0:
            self.y_offset_bottom = abs(ball_y * 2)

        elif ball_y > 0:
            self.y_offset_top = abs(ball_y * 2)

        else:
            self.y_offset_top = 0
            self.y_offset_bottom = 0

    def _rotate_image(self, frame, size, degrees=30):
        matrix = cv2.getRotationMatrix2D((size[0] / 2, size[1] / 2), degrees, 1.0)
        rotated = cv2.warpAffine(frame, matrix, (size[0], size[1]))
        return rotated

    def _init_camera(self):
        self._center_camera(self.config.ballOffsetX, self.config.ballOffsetY)
        self.image_size = (
            self.config.width - (self.x_offset_left + self.x_offset_right),
            self.config.height - (self.y_offset_top + self.y_offset_bottom),
        )
        self.rawCapture = PiRGBArray(
            self.camera, (self.config.width, self.config.height)
        )
        self.stream = self.camera.capture_continuous(
            self.rawCapture, format="bgr", use_video_port=True
        )
