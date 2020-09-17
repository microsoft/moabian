# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Shared interfaces
"""

from typing import Dict
from dataclasses import dataclass

from .device import IDevice
from .vector2 import Vector2
from .common import CircleFeature
from .event import IEventListener


class IController(IEventListener):
    @dataclass
    class Config(IDevice):
        maxAngle: int = 15

    def __init__(self, config: Config, device: IDevice):
        self.config = config

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedMs: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        return Vector2(0, 0)
