# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Calibration Controller

Use CalibrationDetector and perform calibration for plate and ball detection
"""

import os
import pwd
import json
import math
import time
import logging as log

from copy import copy
from enum import Enum
from dataclasses import asdict
from typing import Dict, Optional, cast

from ..device import Device
from ..detectors import HSVDetector
from ..common.common import CircleFeature
from ..config import calibration_path, moab_path
from ..common import IController, IDevice, Vector2


class CalibrationState(Enum):
    Start = 0
    WaitUser = 1
    CalibrateHue = 3
    CalibratePos = 4
    Cancel = 5
    Success = 6
    Failure = 7


class HueCalibrationController(IController):
    def __init__(self, config: IController.Config, device: IDevice):
        super().__init__(config, device, hat=None)
        self.config = config

        # plate must be level
        self.hat.set_plate_angles(0, 0)

        # initial state
        self.state = CalibrationState.Start
        self.found_ball = False
        self.hue_low = 180
        self.hue_high = 0
        self.hue_steps = 20

        # make a copy for the new settings
        self.calibration = device.calibration
        self.new_calibration = copy(device.calibration)
        self.ball_detector: Optional[HSVDetector] = None

    # cancel without calibrating
    def on_menu_down(self, sender: IDevice):
        self.state = CalibrationState.Cancel
        sender.stop()

        # Hover the plate and deactivate the servos
        self.hat.hover_plate()
        time.sleep(0.5)
        self.hat.disable_servo_power()
        time.sleep(0.5)

    def on_joy_down(self, sender: IDevice):
        if self.state == CalibrationState.WaitUser:
            self.state = CalibrationState.CalibrateHue

    def getControlOutput(
        self,
        sender: Device,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:
        """
        This state machine asks the user to place the ball in the center of the plate.

        - It then sweeps through the Hue spectrum looking for balls of different colors.
        - It takes the center average of the found balls by color and uses that as the
        ballHue.
        - It then uses that hue to find the center of the ball, which becomes the new plate center.
        """
        # init
        if self.ball_detector is None:
            self.ball_detector = cast(HSVDetector, sender.detectors["ball"])

            # make sure we don't use the last calibration settings
            # while trying to find the current calibration settings
            self.ball_detector.calibration.plateXOffset = 0.0
            self.ball_detector.calibration.plateYOffset = 0.0

        if self.state == CalibrationState.Start:
            self._start_calibration()

        # walk each hue and try and detect a ball
        if self.state == CalibrationState.CalibrateHue:
            result = detectorResults.get("ball", None)
            frameSize = sender.sensor.config.height
            self._calibrate_hue(result, frameSize)

        # once we've found a ball hue, find the center
        if self.state == CalibrationState.CalibratePos:
            result = detectorResults.get("ball", None)
            frameSize = sender.sensor.config.height
            self._calibrate_pos(result, frameSize)

        # user cancelled
        if self.state == CalibrationState.Cancel:
            pass

        # found a ball, write out hue
        if self.state == CalibrationState.Success:
            self._calibration_success(sender)

        # detect failed
        if self.state == CalibrationState.Failure:
            self._calibration_failure(sender)

        return Vector2(0, 0)

    def _start_calibration(self):
        if self.ball_detector:
            self.hat.set_icon_text(self.hat.Icon.BLANK, self.hat.Text.CAL_INSTR)

            # start search here
            self.found_ball = False
            self.hue_low = 180
            self.hue_high = 0
            self.hue_steps = 20
            self.count = 0
            self.ball_detector.config.hue = int(180 / self.hue_steps)
            self.state = CalibrationState.WaitUser

    def _ball_close_enough(self, feature: Optional[CircleFeature], frameSize: int):
        centerX = feature.center.x / frameSize
        centerY = feature.center.y / frameSize
        radius = feature.radius / frameSize

        # reject balls which are too far from the center and too small
        MAX_BALL_DIST = 0.2
        MIN_BALL_SIZE = 0.05
        return (
            math.fabs(centerX) < MAX_BALL_DIST
            and math.fabs(centerY) < MAX_BALL_DIST
            and radius > MIN_BALL_SIZE
        )

    def _calibrate_hue(self, result: Optional[CircleFeature], frameSize: int):
        # if we found a ball roughly in the center and large enough...
        if result and self._ball_close_enough(result, frameSize):
            self.found_ball = True

            self.hue_low = min(self.hue_low, self.ball_detector.config.hue)
            self.hue_high = max(self.hue_high, self.ball_detector.config.hue)

        # rotate through hues
        self.ball_detector.config.hue += int(180 / self.hue_steps)

        # after we've swept the whole hue range...
        if self.ball_detector.config.hue >= 180:
            log.info(f"Hue range: [{self.hue_low} .. {self.hue_high}]")
            if self.found_ball:
                # use the center of the detected ball hues
                self.new_calibration.ballHue = int((self.hue_low + self.hue_high) / 2)
                log.info(f"Hue calibrated: {self.new_calibration.ballHue}")

                # set up the hue for the position calibration
                self.ball_detector.config.hue = self.new_calibration.ballHue
                self.found_ball = False
                self.state = CalibrationState.CalibratePos
            else:
                log.warn(f"Hue calibrated failed.")
                self.state = CalibrationState.Failure

    def _calibrate_pos(self, result: Optional[CircleFeature], frameSize: int):
        if result:
            # if we found a ball roughly in the center and large enough...
            if self._ball_close_enough(result, frameSize):
                self.found_ball = True

                # center of plate is in range [-frameSize/2 .. frameSize/2]
                centerX = result.center.x / frameSize
                centerY = result.center.y / frameSize

                self.new_calibration.plateXOffset = round(centerX, 3)
                self.new_calibration.plateYOffset = round(centerY, 3)
                log.info(
                    f"Offset calibrated: [{self.new_calibration.plateXOffset:.3f}, {self.new_calibration.plateYOffset:.3f}]"
                )

                self.state = CalibrationState.Success

            # try and detect for 20 frames before giving up
            elif self.count > 20:
                log.warn(f"Offset calibrated failed.")
                self.state = CalibrationState.Failure

            self.count += 1

    def _calibration_success(self, sender: Device):
        log.info("Calibration Success.")
        self._print_results()
        self._write_calibration(sender)

        self.hat.set_icon_text(self.hat.Icon.CHECK, self.hat.Text.CAL_COMPLETE)
        time.sleep(2)

        sender.stop()

    def _calibration_failure(self, sender: Device):
        log.warn("Failed to calibrate.")
        self._print_results()

        self.hat.set_icon_text(self.hat.Icon.BLANK, self.hat.Text.ERROR)
        time.sleep(2)

        sender.stop()

    def _print_results(self):
        log.info(
            f"center:[{self.new_calibration.plateXOffset}, {self.new_calibration.plateYOffset}] "
            f"hue: {self.new_calibration.ballHue}"
        )

    def _write_calibration(self, sender: Device):
        log.info("write_calibration")
        # move the values from new_calibration to calibration
        # gotta be careful not to move the *instance*, but the values
        self.calibration.plateXOffset = self.new_calibration.plateXOffset
        self.calibration.plateYOffset = self.new_calibration.plateYOffset
        self.calibration.ballHue = self.new_calibration.ballHue

        # Moab controller runs as root (simply for SPI access)
        # but we want to save confg as user so its editable by the "pi" user
        # Better solution is to get from Dockerfile ENV variable or infer
        # from existing folder permissions, but for now,
        # 1000:1000 is the well-known default "pi" user in Raspbian
        uid = 1000
        gid = 1000

        # create `.moab` if it doesn't exist
        if not os.path.exists(moab_path):
            os.makedirs(moab_path)
            log.info(f"Creating folder {moab_path}")
            os.chown(moab_path, uid, gid)

        # write out stuff
        with open(calibration_path, "w+") as outfile:
            log.info(f"Creating calibration file {calibration_path}")
            json.dump(asdict(self.calibration), outfile, indent=4, sort_keys=True)

        # set permisions so user can use
        os.chown(calibration_path, uid, gid)
