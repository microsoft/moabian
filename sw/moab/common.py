import math
from dataclasses import dataclass, field


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"X: {self.x:2.3f}, Y: {self.y:2.3f}"

    def __add__(self, o):
        return Vector2(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Vector2(self.x - o.x, self.y - o.y)

    def __truediv__(self, o):
        return Vector2(self.x / o, self.y / o)

    def __mul__(self, o):
        return Vector2(self.x * o, self.y * o)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        length = self.length()
        if length != 0.0:
            return Vector2(self.x / length, self.y / length)
        else:
            return Vector2(0, 0)

    def dot(self, o):
        return self.x * o.x + self.y * o.y

    def angle(self, o):
        return math.acos(self.dot(o) / self.length() * o.length())

    def distance(self, o):
        return (self - o).length()

    def rotate(self, theta, o=None):
        """ Return a point rotated `theta` radians around `o` """
        if o is None:
            o = Vector2(0, 0)
        x = o.x + math.cos(theta) * (self.x - o.x) - math.sin(theta) * (self.y - o.y)
        y = o.y + math.sin(theta) * (self.x - o.x) + math.cos(theta) * (self.y - o.y)
        return Vector2(x, y)

    def __iter__(self):
        yield self.x
        yield self.y

    def to_int_tuple(self):
        return (int(self.x), int(self.y))


@dataclass
class CircleFeature:
    center: Vector2 = Vector2(0, 0)
    radius = 0.0


@dataclass
class Calibration:
    ball_hue = 22
    plate_y_offset = 0.0  # -0.016
    plate_x_offset = 0.0  # -0.092
    rotation = -30.0
