# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
HSV filtering ball detector
"""

import math
from typing import List, Optional
from dataclasses import dataclass, field

import cv2
import numpy as np
from pymoab import hue_mask

from ..common import CircleFeature, IDetector, IDevice, Vector2
from ..debug import *
from ..device import Device
from ..perfcounters import (
    FrequencyCounter,
    WindowedAverageCounter,
    PerformanceCounters as counter,
)


class HSVDetector(IDetector):
    @dataclass
    class Config(IDetector.Config):
        kernelSize: List[int] = field(default_factory=lambda: [5, 5])
        ballMin: float = 0.06
        ballMax: float = 0.22
        debug: bool = False
        hue: Optional[int] = None  # hue [0..255]
        sigma: float = 0.05  # narrow: 0.01, wide: 0.1
        bandpassGain: float = 12.0
        maskGain: float = 4.0

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config
        self.calibration = device.calibration

        # if we haven't been overridden, use ballHue from
        # the calibration settings.
        if self.config.hue is None:
            self.config.hue = self.calibration.ballHue

        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, tuple(self.config.kernelSize)
        )

        if device.debug_decorator is not None:
            self.x_obs = 0
            self.y_obs = 0
            self.lastDetected = CircleFeature()
            device.debug_decorator.addCallback(self._debugDraw)

    def _debugDraw(self, args):
        img = args[SENSOR_IMG_ARG]
        f = self.lastDetected
        if f is not None:
            center = (int(self.x_obs), int(self.y_obs))
            cv2.circle(img, center, 2, (255, 0, 255), 2)
            cv2.circle(img, center, int(f.radius), (255, 0, 255), 2)

    def detect(
        self, sender: Device, img: np.ndarray, plate_angles: Vector2
    ) -> CircleFeature:
        if img is not None:
            # covert to HSV space
            color = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # 0 == red
            if self.config.hue is None:
                self.config.hue = 0

            # run through each triplet and perform our masking filter on it.
            # hue_mask coverts the hsv image into a grayscale image with a
            # bandpass applied centered around hue, with width sigma
            hue_mask(
                color,
                self.config.hue,
                self.config.sigma,
                self.config.bandpassGain,
                self.config.maskGain,
            )

            # TODO only make this call if X11 debugger
            #if self.config.debug
            #    cv2.imshow("hue_mask", color)

            # convert to b&w mask from grayscale image
            mask = cv2.inRange(
                color, np.array((200, 200, 200)), np.array((255, 255, 255))
            )

            # expand b&w image with a dialation filter
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)

            # TODO only make this call if X11 debugger
            #if self.config.debug:
            #    cv2.imshow("mask", mask)

            contours = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            if len(contours) > 0:
                contour_peak = max(contours, key=cv2.contourArea)
                ((self.x_obs, self.y_obs), radius) = cv2.minEnclosingCircle(
                    contour_peak
                )

                # Determine if ball size is the appropriate size
                frameSize = sender.sensor.config.height
                norm_radius = radius / frameSize
                if self.config.ballMin < norm_radius < self.config.ballMax:
                    counter.update("hit", 1, FrequencyCounter)

                    # rotate the center coords into sensor coords
                    # the ball detector uses rotate coordinates, so we must as well
                    rot_center = Vector2(
                        self.calibration.plateXOffset, self.calibration.plateYOffset
                    ).rotate(math.radians(-self.calibration.rotation))

                    x_center = (rot_center.x + 0.5) * frameSize
                    y_center = (rot_center.y + 0.5) * frameSize

                    # Convert from pixels to absolute with 0,0 as center of detected plate
                    x = self.x_obs - x_center
                    y = self.y_obs - y_center
                    self.lastDetected = CircleFeature(Vector2(x, y), radius)
                    return self.lastDetected
                else:
                    counter.update("miss", 1, FrequencyCounter)

            counter.update("hit", 0, FrequencyCounter)
            counter.update("miss", 0, FrequencyCounter)

        return CircleFeature()
