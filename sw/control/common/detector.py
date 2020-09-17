# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Shared interfaces
"""

import math
import numpy as np
from dataclasses import dataclass


from .device import IDevice
from .vector2 import Vector2
from .common import CircleFeature


class IDetector:
    @dataclass
    class Config:
        pass

    def __init__(self, config: Config, device: IDevice):
        self.calibration = device.calibration

    def detect(
        self, sender: IDevice, img: np.ndarray, plate_angles: Vector2
    ) -> CircleFeature:
        """
        Your detection code goes here.
        """
        return CircleFeature()

    def post_detect(self, feature: CircleFeature) -> CircleFeature:
        """
        Do some post processing on the detected feature.
        You shouldn't need to overload this.
        """
        if feature:
            feature.center = feature.center.rotate(
                math.radians(self.calibration.rotation)
            )
        return feature
