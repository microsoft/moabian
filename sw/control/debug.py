# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from .common import IDebugDecorator
import cv2
import os
import pathlib
import logging as log


SENSOR_IMG_ARG = "sensor_img"


class CallbackDecorator(IDebugDecorator):
    def __init__(self, config: dict):
        super().__init__(config)
        self.callbacks = []

    def addCallback(self, fn):
        self.callbacks.append(fn)

    def decorate(self, args):
        for callback in self.callbacks:
            callback(args)


class X11Decorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        cv2.namedWindow(self.config["windowName"])

    def decorate(self, args):
        super().decorate(args)

        cv2.imshow(self.config["windowName"], args[SENSOR_IMG_ARG])
        cv2.waitKey(1) & 0xff

    def __del__(self):
        cv2.destroyAllWindows()


class FileDecorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        self.filename = self.config["filename"]
        self.disable = False

        # Create path to filename in case it doesn't exist
        dirname = os.path.dirname(self.filename)
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

        log.info(f"Saving camera frame to {self.filename}")

    def decorate(self, args):
        super().decorate(args)

        if self.disable:
            return

        try:
            image = args[SENSOR_IMG_ARG]
            cv2.imwrite(self.filename, image, [cv2.IMWRITE_JPEG_QUALITY, 70])

        except Exception as ex:
            self.disable = True
            log.error(ex)
