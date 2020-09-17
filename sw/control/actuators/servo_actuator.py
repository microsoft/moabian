# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Servo actuator
"""

import pymoab
from numpy import int8

from ..common import IActuator, IDevice, Vector2


class ServoActuator(IActuator):
    def __init__(self, config: IActuator.Config, device: IDevice):
        super().__init__(config, device)
        self.config = config
        self.calibration = device.calibration

        pymoab.setServoOffsets(
            self.calibration.servoOffsets[0],
            self.calibration.servoOffsets[1],
            self.calibration.servoOffsets[2],
        )
        pymoab.activatePlate()

        self.setPlateAngles(device, Vector2(0, 0))

    def __del__(self):
        pymoab.hoverPlate()

    def setPlateAngles(self, sender: IDevice, plate_angles: Vector2):
        self.lastSetPlateAngles = plate_angles
        pymoab.setPlateAngles(int(plate_angles.x), int(plate_angles.y))

    def getLastSetPlateAngles(self) -> Vector2:
        return self.lastSetPlateAngles
