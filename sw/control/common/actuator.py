# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Actuator interface
"""

from dataclasses import dataclass

from .device import IDevice
from .vector2 import Vector2


class IActuator:
    @dataclass
    class Config:
        pass

    def __init__(self, config: Config, device: IDevice):
        self.config = config

    def setPlateAngles(self, sender: IDevice, plate_angles: Vector2):
        pass

    def getLastSetPlateAngles(self) -> Vector2:
        return Vector2(0, 0)
