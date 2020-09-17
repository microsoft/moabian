# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Basic color classes
"""

from typing import Tuple
from dataclasses import dataclass


@dataclass
class RGBColor:
    r: int
    g: int
    b: int

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = r
        self.g = g
        self.b = b

    def __init__(self, rgb: Tuple[int, int, int]):
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]

    def __str__(self):
        return f"R: {self.r}, G: {self.g}, B: {self.b}"

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b


@dataclass
class HSVColor:
    h: int
    s: int
    v: int

    def __init__(self, h: int = 0, s: int = 0, v: int = 0):
        self.h = h
        self.s = s
        self.v = v

    def __init__(self, hsv: Tuple[int, int, int]):
        self.h = hsv[0]
        self.s = hsv[1]
        self.v = hsv[2]

    def __str__(self):
        return f"H: {self.h:.4f}, S: {self.s:.4f}, V: {self.v:.4f}"

    def __iter__(self):
        yield self.h
        yield self.s
        yield self.v
