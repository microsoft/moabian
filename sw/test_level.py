# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from hat import Hat

with Hat() as hat:
    hat.enable_servos()
    hat.set_angles(0, 0)

    input("Hit ENTER to stop...")
    hat.go_down()
