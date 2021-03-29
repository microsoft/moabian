# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from hat import Hat
from time import sleep


def test_display():
    with Hat() as hat:
        hat.enable_servos()
        sleep(0.5)

        angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

        for angle in angles:
            hat.set_angles(angle[0], angle[1])
            sleep(0.5)


if __name__ == "__main__":
    print(test_display())
