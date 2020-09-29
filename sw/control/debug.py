# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import cv2

from .common import IDebugDecorator
import logging as log
import imagezmq

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


class MQDecorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        w = self.config["width"]
        h = self.config["height"]
        log.info(f"Starting camera streaming w={w} h={h}")

        uri = "tcp://192.168.1.128:5555"
        self.queue = imagezmq.ImageSender(connect_to=uri)

    def decorate(self, args):
        super().decorate(args)

        if self.queue is not None:
            try:
                frame = args[SENSOR_IMG_ARG]
                ret, jpg = cv2.imencode(".jpg", frame,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                self.queue.send_jpg("moab", jpg)
            except Exception as ex:
                log.warn("Exception1")

        else:
            log.warn("queue is none")


