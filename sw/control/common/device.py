# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Shared interfaces
"""

import logging as log
from pydoc import locate
from dacite import from_dict
from dataclasses import dataclass, field
from typing import List, Optional, Union, cast

from .common import IDebugDecorator


"""
Component config is either a string of the name of component to load.
Example:
    {
        "mycomponent" : "my.namespace.MyController",
        ...
    }

Or it is a dictionary with a `name` field and parameter overrides for the defaults.
Example:
    {
        "mycomponent": {
            "name": "my.namespace.MyController",
            "someParam": 42.0
        },
        ...
    }

"""
ComponentConfig = Union[dict, str]


class IDevice:
    @dataclass
    class Calibration:
        servoOffsets: List[int] = field(default_factory=lambda: [0, 0, 0])

        # plate calibration as a percentage of frame size
        plateXOffset: float = 0.0
        plateYOffset: float = 0.0

        ballHue: int = 32  # orange/yellow
        rotation: float = -30.0  # the camera sits -30deg rotated from plate coords

    @dataclass
    class Config:
        frequencyHz: float = 30.0
        joystickThreshold: float = 0.8
        menu_idx: int = 0
        debug: bool = False
        debugDecorator: Optional[ComponentConfig] = None
        sensor: Optional[ComponentConfig] = None
        detectors: Optional[ComponentConfig] = None
        controller: Optional[ComponentConfig] = None
        actuator: Optional[ComponentConfig] = None

    def __init__(
        self,
        config: Config,
        calibration: Calibration,
        debug_decorator: Optional[IDebugDecorator],
    ):
        self.debug_decorator = debug_decorator
        self.config = config

        # shared per-machine calibration data
        self.calibration = calibration
        self.next_device: Optional[str] = None
        self.previous_menu: int = self.config.menu_idx

    def update(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass

    def set_next_device(self, device_name: str):
        self.next_device = device_name

    def get_next_device(self) -> Optional[str]:
        return self.next_device

    def component_from_config(
        self, component_config: ComponentConfig, **kwargs
    ) -> Optional[object]:
        """
        Import classes with the following signature,
        and construct them with their config class.

        Then add any additional params to their class

            class Foo:
                @dataclass
                class Config:
                    param1: type = default
                    param2: type = default
                    ...
                def __init__(self, config: Config):
                    ...
        """
        class_name = ""
        config = {}
        try:
            # if we're just a string expand out into a dict with no config
            if type(component_config) is str:
                class_name = cast(str, component_config)
            elif type(component_config) is dict:
                class_name = cast(dict, component_config)["name"]
                config = component_config

            # locate class ref for module.name.Foo and module.name.Foo.Config
            class_ref = locate(class_name, forceload=False)
            config_ref = locate(class_name + ".Config", forceload=False)

            # unpack dict into dataclass
            config_inst = from_dict(config_ref, config)
            ref = class_ref(config_inst, self)  # type: ignore
        except Exception as e:
            log.exception(f"Error creating class {class_name}\n{e}")
            return None

        return ref
