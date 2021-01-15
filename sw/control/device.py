# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import numpy as np
from enum import Enum
from pydoc import locate
from control.hat import interface as hat
from typing import Any, Callable, Dict, Optional, cast

from .debug import *
from .timers import BusyTimer
from .common.event import EventDispatcher
from .perfcounters import WindowedAverageCounter, PerformanceCounters as counter
from .common import IActuator, IController, IDetector, IDevice, ISensor, Vector2

InputHandler = Callable[[bool, bool, int, int], None]


class JoystickYDir(Enum):
    Unset = 0
    Center = 0
    Up = 1
    Down = 2


class Device(IDevice):
    def __init__(
        self,
        config: IDevice.Config,
        calibration: IDevice.Calibration,
        inputHandler: InputHandler = None,
        debugDecorator: Optional[IDebugDecorator] = None,
    ):
        super().__init__(config, calibration, debugDecorator)
        self.config = config

        self.inputHandler = inputHandler

        self.sensor: Optional[ISensor] = None
        self.detectors: Optional[Dict[str, IDetector]] = None
        self.controller: Optional[IController] = None
        self.actuator: Optional[IActuator] = None

        self.runloop = BusyTimer()
        self.running = False

        # listeners get added in createFromConfig...
        self.events = EventDispatcher()

    def update(self):

        # get input IO and dispatch it to listeners
        event = self.events.get_next_event()
        if event is not None:
            self.events.dispatch_event(self, event)

        # check if we should still run after processing events
        if self.runloop.running:
            # get sensor data
            elapsedSec: float = 0
            img: Optional[np.ndarray] = None

            if self.sensor:
                counter.start("sensor", WindowedAverageCounter)
                elapsedSec, img = self.sensor.getNextInput(self)
                counter.stop()

            # fetch previous plate angles if we have an actuator
            lastPlateAngles = Vector2(0, 0)
            if self.actuator:
                lastPlateAngles = self.actuator.getLastSetPlateAngles()

            # pass sensor output to various detectors
            detectorResults: Dict[str, Any] = {}
            if self.detectors and img is not None:
                for detectorName in self.detectors:
                    detector = self.detectors[detectorName]

                    counter.start(detectorName, WindowedAverageCounter)
                    feature = detector.detect(self, img, lastPlateAngles)
                    detectorResults[detectorName] = detector.post_detect(feature)
                    counter.stop()

            # run the controller
            output = self.controller.getControlOutput(
                self, elapsedSec, detectorResults, lastPlateAngles
            )

            # actuate
            if self.actuator:
                self.actuator.set_plate_angles(self, output)

            # and execute debuging decorators
            if self.config.debug:
                if self.debug_decorator is not None:
                    self.debug_decorator.decorate({SENSOR_IMG_ARG: img})

    def run(self):
        if self.sensor:
            self.sensor.start()

        # The control loop needs to run slightly faster than the camera capture rate.
        # The camera capture rate needs to be slightly slower than the controller execution time.
        #
        # If they run too close together the camera may give us stale frames and the controllers
        # will lose stability (positive feedback loop that causes the ball to drop).
        #
        # Suggest improvement to sync with the video capture buffer instead
        controlHz = self.config.frequencyHz + 5
        self.runloop.start(1.0 / (controlHz), self.update)

    def stop(self):
        self.runloop.stop()
        if self.sensor:
            self.sensor.stop()

    @staticmethod
    def createFromConfig(
        config: IDevice.Config,
        calibration: IDevice.Calibration,
        inputHandler: InputHandler = None,
    ) -> Optional[IDevice]:

        # optional debug decorator
        debug_decorator: Optional[IDebugDecorator] = None
        if config.debug and config.debugDecorator:
            debug_class = cast(dict, config.debugDecorator)["name"]
            decorator_ref = locate(debug_class, forceload=True)
            debug_decorator = decorator_ref(config.debugDecorator)  # type: ignore

        # create device
        device = Device(config, calibration, inputHandler, debug_decorator)

        # sensor
        sensor: Optional[ISensor] = None
        if config.sensor:
            sensor = cast(
                ISensor,
                device.component_from_config(config.sensor),
            )

        # unpack the detectors
        detectors: Optional[Dict[str, IDetector]] = None
        if config.detectors:
            detectors = {}
            for name in cast(dict, config.detectors):
                detector_config = config.detectors[name]
                detector = cast(
                    IDetector, device.component_from_config(detector_config)
                )
                detectors[name] = detector

        # controller
        controller: Optional[IController] = None
        if config.controller:
            controller = cast(
                IController,
                device.component_from_config(config.controller),
            )

            # register for events
            device.events.listeners.append(controller)
        else:
            raise Exception("You must specifiy a controller")

        # actuator
        actuator: Optional[IActuator] = None
        if config.actuator:
            actuator = cast(
                IActuator,
                device.component_from_config(config.actuator),
            )

        # set 'em
        device.sensor = sensor
        device.detectors = detectors
        device.controller = controller
        device.actuator = actuator

        return device
