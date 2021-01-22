# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Servo actuator
"""

from numpy import int8

from ..common import IActuator, IDevice, Vector2


class ServoActuator(IActuator):
    def __init__(self, config: IActuator.Config, device: IDevice):
        super().__init__(config, device, hat=None)
        self.config = config
        self.calibration = device.calibration

    def init_hat(self):
        self.hat.set_servo_offsets(
            self.calibration.servoOffsets[0],
            self.calibration.servoOffsets[1],
            self.calibration.servoOffsets[2],
        )
        self.hat.activate_plate()
        self.set_plate_angles(Vector2(0, 0))

    def set_plate_angles(self, plate_angles: Vector2):
        self.lastSetPlateAngles = plate_angles
        self.hat.set_plate_angles(int(plate_angles.x), int(plate_angles.y))

    def getLastSetPlateAngles(self) -> Vector2:
        return self.lastSetPlateAngles
