# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import socket
import os

from time import sleep
from typing import Dict
from control.hat import interface as hat

from ..common import IController, IDevice, CircleFeature, Vector2
import logging as log


class InfoController(IController):
    def __init__(self, config: IController.Config, device: IDevice):
        super().__init__(config, device)
        """Print out the IP address and SW version when user enters InfoController"""

        hat.print_info_screen()

    def on_menu_down(self, sender: IDevice):
        sender.stop()

        # Hover the plate and deactivate the servos
        hat.hover_plate()
        time.sleep(0.5)
        hat.disable_servo_power()
        time.sleep(0.5)

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        return Vector2(0, 0)
