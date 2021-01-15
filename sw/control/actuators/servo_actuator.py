# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Servo actuator
"""

from numpy import int8
from control.hat import interface as pymoab

from ..common import IActuator, IDevice, Vector2


class ServoActuator(IActuator):
    def __init__(self, config: IActuator.Config, device: IDevice):
        super().__init__(config, device)
        self.config = config
        self.calibration = device.calibration

        pymoab.set_servo_offsets(
            self.calibration.servoOffsets[0],
            self.calibration.servoOffsets[1],
            self.calibration.servoOffsets[2],
        )
        pymoab.activate_plate()

        self.set_plate_angles(device, Vector2(0, 0))

    def __del__(self):
        pymoab.hover_plate()

    def set_plate_angles(self, sender: IDevice, plate_angles: Vector2):
        self.lastSetPlateAngles = plate_angles
        pymoab.set_plate_angles(int(plate_angles.x), int(plate_angles.y))

    def getLastSetPlateAngles(self) -> Vector2:
        return self.lastSetPlateAngles
