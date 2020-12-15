from time import sleep
from typing import Dict

import time
import pymoab

from ..common import IController, IDevice, CircleFeature, Vector2


class InfoController(IController):
    def __init__(self, config: IController.Config, device: IDevice):
        super().__init__(config, device)
        """Print out the IP address and SW version when user enters InfoController"""
        pymoab.printIP()
        pymoab.printSWVersion()

        pymoab.setIcon(pymoab.Icon.DOT)
        pymoab.setText(pymoab.Text.VERS_IP_SN)
        pymoab.sync()

    def on_menu_down(self, sender: IDevice):
        sender.stop()

        # Hover the plate and deactivate the servos
        pymoab.hoverPlate()
        pymoab.sync()
        sleep(0.5)
        pymoab.disableServoPower()
        pymoab.sync()
        sleep(0.5)

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        return Vector2(0,0)

