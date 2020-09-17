# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import cv2

from .common import IDebugDecorator


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
        cv2.waitKey(1) & 0xFF

    def __del__(self):
        cv2.destroyAllWindows()
