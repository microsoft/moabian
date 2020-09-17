# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Basic 2D vector class
"""

import math
from typing import Tuple, Optional


class Vector2:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"X: {self.x:2.3f}, Y: {self.y:2.3f}"

    def __add__(self, o: "Vector2"):
        return Vector2(self.x + o.x, self.y + o.y)

    def __sub__(self, o: "Vector2"):
        return Vector2(self.x - o.x, self.y - o.y)

    def __truediv__(self, o: float):
        return Vector2(self.x / o, self.y / o)

    def __mul__(self, o: float):
        return Vector2(self.x * o, self.y * o)

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        length = self.length()
        if length != 0.0:
            return Vector2(self.x / length, self.y / length)
        else:
            return Vector2(0, 0)

    def dot(self, o: "Vector2") -> float:
        return self.x * o.x + self.y * o.y

    def angle(self, o: "Vector2") -> float:
        return math.acos(self.dot(o) / self.length() * o.length())

    def distance(self, o: "Vector2") -> float:
        return (self - o).length()

    def rotate(self, theta: float, o: Optional["Vector2"] = None) -> "Vector2":
        """
        Return a point rotated `theta` radians around `o`
        """
        if o is None:
            o = Vector2(0, 0)
        x = o.x + math.cos(theta) * (self.x - o.x) - math.sin(theta) * (self.y - o.y)
        y = o.y + math.sin(theta) * (self.x - o.x) + math.cos(theta) * (self.y - o.y)
        return Vector2(x, y)

    def __iter__(self):
        yield self.x
        yield self.y

    def toIntTuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))
