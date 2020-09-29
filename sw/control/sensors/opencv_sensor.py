# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
A sensor that uses OpenCV for capture
"""

from dataclasses import dataclass
from ..common import ISensor, IDevice

import cv2
import threading
import numpy as np

from time import time
from typing import Tuple, Optional


# Link to raspicam_cv implementation for mapping values
# https://github.com/cedricve/raspicam/blob/651c56418a5a594fc12f1414eb14f2b899729cb1/src/raspicam_cv.h#L108

class OpenCVCameraSensor(ISensor):
    @dataclass
    class Config(ISensor.Config):
        deviceId: int = 0
        width: int = 256
        height: int = 256
        rotation: float = 0
        brightness: int = 50
        contrast: int = 100
        saturation: int = 100
        gain: int = 100
        fps: Optional[int] = None

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config
        self.prevTime = 0.0

        # set the camera capture frequency to the control frequency
        if self.config.fps is None:
            self.fps = device.config.frequencyHz
        else:
            self.fps = self.config.fps

        self.source: Optional[cv2.VideoCapture] = None
        self.last_frame: Optional[np.ndarray] = None

        # TODO: move init_debug into X11 debug handler version only
        self._init_debug(device)

    def start(self):
        self.source = cv2.VideoCapture(self.config.deviceId)
        if self.source:
            self.source.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.source.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.source.set(cv2.CAP_PROP_FPS, self.fps)

            # Not meant to be configurable
            self.source.set(cv2.CAP_PROP_MODE, 0)

            # initial settings
            self.setBrightness(self.config.brightness)
            self.setContrast(self.config.contrast)
            self.setSaturation(self.config.saturation)
            self.setGain(self.config.gain)
        else:
            raise Exception("Couldn't create camera.")

    def stop(self):
        if self.source:
            self.source.release()
            self.source = None

    def getNextInput(self, sender: IDevice) -> Tuple[float, Optional[np.ndarray]]:
        # safety check
        if self.source is None:
            raise Exception("Using camera before it has been started.")

        # Calculate the time elapsed since the last sensor snapshot
        currTime = time()
        elapsedTime = currTime - self.prevTime
        self.prevTime = currTime

        ret, frame = self.source.read()
        if ret:
            return elapsedTime, frame

        return elapsedTime, None

    def setBrightness(self, b: int):
        self.config.brightness = b
        if self.source:
            self.source.set(cv2.CAP_PROP_BRIGHTNESS, self.config.brightness)

    def setContrast(self, c: int):
        self.config.contrast = c
        if self.source:
            self.source.set(cv2.CAP_PROP_CONTRAST, self.config.contrast)

    def setSaturation(self, s: int):
        self.config.saturation = s
        if self.source:
            self.source.set(cv2.CAP_PROP_CONTRAST, self.config.saturation)

    def setGain(self, g: int):
        self.config.gain = g
        if self.source:
            self.source.set(cv2.CAP_PROP_CONTRAST, self.config.gain)

    # debug stuff
    def _init_debug(self, device: IDevice):
        if device.config.debug and device.debug_decorator:
            cv2.createTrackbar(
                "brightness",
                "frame",
                self.config.brightness,
                100,
                lambda b: self.setBrightness(b),
            )
            cv2.createTrackbar(
                "contrast",
                "frame",
                self.config.contrast,
                100,
                lambda c: self.setContrast(c),
            )
            cv2.createTrackbar(
                "saturation",
                "frame",
                self.config.saturation,
                100,
                lambda c: self.setSaturation(c),
            )
            cv2.createTrackbar(
                "gain", "frame", self.config.gain, 100, lambda c: self.setGain(c)
            )
