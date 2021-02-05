from time import sleep
from typing import Dict

import time
import pymoab
import socket
import os

from ..common import IController, IDevice, CircleFeature, Vector2
import logging as log

class InfoController(IController):
    def __init__(self, config: IController.Config, device: IDevice):
        super().__init__(config, device)
        """Print out the IP address and SW version when user enters InfoController"""

        # IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 1))
        ip = s.getsockname()[0]       # returns string like '1.2.3.4'
        ip_quads = [int(b) for b in ip.split(".")]
        log.info(f"IP: {ip}")
        pymoab.showIP(*ip_quads)

        # Version
        ver_string = os.environ.get("MOABIAN", "2.5.0")
        ver_quad = [int(b) for b in ver_string.split(".")]
        log.info(f"Version string: {ver_string}")
        log.info(f"Version quad: {ver_quad}")
        pymoab.showVersion(*ver_quad)

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

