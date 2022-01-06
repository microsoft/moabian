# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import colorsys


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.0)  # XXX assume int() truncates!
    f = (h * 6.0) - i
    p, q, t = v * (1.0 - s), v * (1.0 - s * f), v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


def rgb_to_bgr(rgb):
    return rgb[::-1]


def hue_to_bgr(hue, s=0.75, v=0.75):
    assert hue >= 0 and hue <= 360

    rgb = hsv_to_rgb(hue / 360.0, s, v)
    rgb = [int(c * 255) for c in rgb]
    return rgb_to_bgr(rgb)


def hsv_normalized_to_bgr(h, s, v):
    assert 0 <= h <= 1.0
    assert 0 <= s <= 1.0
    assert 0 <= v <= 1.0

    def h2r(h, s, v):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    return rgb_to_bgr(h2r(h, s, v))


# HSV was invented by Alvy Ray Smith (cool!)


def test_code(t, e):
    v = hsv_to_rgb(*t)
    y = [int(s * 255) for s in v]
    print(f"f({t}) = {y} ~= expected: {e}")
    return y == e


if __name__ == "__main__":

    # 45 = orange
    test_code((45 / 360.0, 1.0, 0.5), [128, 96, 0])

    # 45 = orange
    test_code((45 / 360.0, 0.75, 0.5), [218, 165, 32])

    # 157 = green
    test_code((45 / 360.0, 1.0, 0.5), [128, 96, 0])

    # 211 = blue
    test_code((211 / 360.0, 1.0, 0.5), [0, 61, 128])

    # 0, 100%, 100% = red
    test_code((1, 1.0, 1.0), [255, 4, 0])
    test_code((0 / 360.0, 1.0, 1.0), [255, 0, 0])

    print(hue_to_bgr(45))
