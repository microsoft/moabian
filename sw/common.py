# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import math
import json
import logging as log

from dataclasses import dataclass


def high_pass_filter(frequency, fc=50):
    x_dot_cstate = 0

    def hpf(x):
        nonlocal x_dot_cstate  # allow x_dot_cstate to be updated in inner scope
        x_dot = -(fc ** 2) * x_dot_cstate + fc * x
        x_dot_cstate += (-fc * x_dot_cstate + x) / frequency
        return x_dot

    return hpf


def low_pass_filter(frequency, fc=50):
    y_prev = 0.0
    dt = 1 / frequency
    tau = 1 / (2 * math.pi * fc)
    alpha = dt / (tau + dt)

    def lpf(x):
        nonlocal y_prev  # allow y_prev to be updated in inner scope
        y = alpha * x + (1 - alpha) * y_prev
        y_prev = y
        return y

    return lpf


def derivative(frequency, fc=None):
    prev_x = 0

    def derivate(x):
        nonlocal prev_x
        x_dot = (x - prev_x) * frequency
        prev_x = x
        return x_dot

    return derivate


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
        """Return a point rotated `theta` radians around `o`"""
        if o is None:
            o = Vector2(0, 0)
        x = o.x + math.cos(theta) * (self.x - o.x) - math.sin(theta) * (self.y - o.y)
        y = o.y + math.sin(theta) * (self.x - o.x) + math.cos(theta) * (self.y - o.y)
        return Vector2(x, y)

    def rotate_deg(self, theta, o=None):
        return self.rotate(math.radians(theta), o=o)

    def __iter__(self):
        yield self.x
        yield self.y

    def __list__(self):
        return [self.x, self.y]

    def __tuple__(self):
        return (self.x, self.y)

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


def write_calibration(calibration_dict, calibration_file="bot.json"):
    print("Writing calibration to file. File is:", calibration_file)
    log.info("Writing calibration.")

    # write out stuff
    with open(calibration_file, "w+") as outfile:
        log.info(f"Creating calibration file {calibration_file}")
        json.dump(calibration_dict, outfile, indent=4, sort_keys=True)

    print("Calibration written.")


def validate_calibration(calibration_dict, calibration_file):
    """Ensure that the calibration is valid. If not fix it."""
    bh = calibration_dict.get("ball_hue")
    po = calibration_dict.get("plate_offsets")
    pix = calibration_dict.get("pixel_offsets")
    so = calibration_dict.get("servo_offsets")

    val_bh = bh is not None and type(bh) == int and 0 <= bh < 360
    # Old calibration files have meter offsets not pixel offsets, ie should not exist
    val_po = po is None
    # New calibration files have pixel offsets
    val_pix = (
        pix is not None
        and (type(pix) == tuple or type(pix) == list)
        and len(pix) == 2
        and type(pix[0]) == int
        and type(pix[1]) == int
    )
    val_so = (
        so is not None
        and (type(so) == tuple or type(so) == list)
        and len(so) == 3
        and (type(so[0]) == int or type(so[0]) == float)
        and (type(so[1]) == int or type(so[1]) == float)
        and (type(so[2]) == int or type(so[2]) == float)
    )
    if not (val_bh and val_po and val_pix and val_so):
        log.info("Calibration file is invalid. Fixing.")
        log.info("Previous calibration:", calibration_dict)

        # Set defaults if something is wrong
        if not val_bh:
            calibration_dict["ball_hue"] = 44
        if not val_po:
            del calibration_dict["plate_offsets"]
        if not val_pix:
            calibration_dict["pixel_offsets"] = (0, 0)
        if not val_so:
            calibration_dict["servo_offsets"] = (0.0, 0.0, 0.0)
        write_calibration(calibration_dict, calibration_file)

        log.info("Fixed calibration:", calibration_dict)

    return calibration_dict


def read_calibration(calibration_file="bot.json"):
    log.info("Reading previous calibration.")

    if os.path.isfile(calibration_file):
        with open(calibration_file, "r") as f:
            calibration_dict = json.load(f)
    else:  # Use defaults
        calibration_dict = {
            "ball_hue": 44,
            "pixel_offsets": (0, 0),
            "servo_offsets": (0.0, 0.0, 0.0),
        }
    calibration_dict = validate_calibration(calibration_dict, calibration_file)
    return calibration_dict