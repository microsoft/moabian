# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Shared interfaces
"""

from dataclasses import dataclass

from .vector2 import Vector2


@dataclass
class CircleFeature:
    center: Vector2 = Vector2(0, 0)
    radius: float = 0.0


class IDebugDecorator:
    def __init__(self, config: dict):
        self.config = config

    def __del__(self):
        pass

    def decorate(self, args):
        pass
