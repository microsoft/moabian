# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Datclasses that contain bounds values
"""

from typing import Optional
from dataclasses import dataclass, field

from .color import HSVColor


@dataclass
class IntBounds:
    min: Optional[int] = 0
    max: Optional[int] = 0


@dataclass
class FloatBounds:
    min: Optional[float] = 0
    max: Optional[float] = 0


@dataclass
class HSVBounds:
    min: Optional[HSVColor] = field(default_factory=lambda: HSVColor((0, 0, 0)))
    max: Optional[HSVColor] = field(default_factory=lambda: HSVColor((0, 0, 0)))
