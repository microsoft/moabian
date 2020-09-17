# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Test cases
"""

# pyright: strict

import math

from ..controllers import BrainController
from ..common import Vector2


# basic test for heading
def test_heading():
    zero = Vector2(0, 0)
    one = Vector2(1, 0)
    heading = BrainController.heading_to_point(zero, Vector2(1.0, 0.0), one)
    assert heading == 0.0, "Expected heading to be 0.0 while moving towards point"

    heading = BrainController.heading_to_point(zero, Vector2(-1.0, 0.0), one)
    assert (
        heading == math.pi
    ), "Expected heading to be math.pi while moving away from point"

    heading = BrainController.heading_to_point(zero, Vector2(0.0, -1.0), one)
    assert (
        heading == -math.pi / 2
    ), "Expected heading to be negative while moving to right of point"

    heading = BrainController.heading_to_point(zero, Vector2(0.0, 1.0), one)
    assert (
        heading == math.pi / 2
    ), "Expected heading to be positive while moving to left of point"
