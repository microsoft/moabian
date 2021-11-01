# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import math
from dataclasses import dataclass


def high_pass_filter(frequency, fc=50):
    x_dot_cstate = 0
    
    def reset():
        nonlocal x_dot_cstate
        x_dot_cstate = 0

    def hpf(x):
        nonlocal x_dot_cstate  # allow x_dot_cstate to be updated in inner scope
        x_dot = -(fc ** 2) * x_dot_cstate + fc * x
        x_dot_cstate += (-fc * x_dot_cstate + x) / frequency
        return x_dot

    return hpf, reset


def low_pass_filter(frequency, fc=50):
    y_prev = 0.0
    dt = 1 / frequency
    tau = 1 / (2 * math.pi * fc)
    alpha = dt / (tau + dt)

    def reset():
        nonlocal y_prev, dt, tau, alpha
        y_prev = 0.0
        dt = 1 / frequency
        tau = 1 / (2 * math.pi * fc)
        alpha = dt / (tau + dt)

    def lpf(x):
        nonlocal y_prev  # allow y_prev to be updated in inner scope
        y = alpha * x + (1 - alpha) * y_prev
        y_prev = y
        return y

    return lpf, reset


def derivative(frequency, fc=None):
    prev_x = 0
    
    def reset():
        nonlocal prev_x
        prev_x = 0

    def derivate(x):
        nonlocal prev_x
        x_dot = (x - prev_x) * frequency
        prev_x = x
        return x_dot

    return derivate, reset


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

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


def polar(x, y, degrees=True):
    r = math.sqrt(x * x + y * y)
    theta = math.atan(y / x)
    if degrees:
        theta *= 180 / np.pi
    return r, theta


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
