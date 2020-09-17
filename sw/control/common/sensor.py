# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Shared interfaces
"""

import numpy as np
from typing import Tuple
from dataclasses import dataclass

from .device import IDevice


class ISensor:
    @dataclass
    class Config(IDevice):
        width: int = 256
        height: int = 256

    def __init__(self, config: Config, device: IDevice):
        self.config = config

    def start(self):
        pass

    def stop(self):
        pass

    def getNextInput(self, sender: IDevice) -> Tuple[float, np.ndarray]:
        return (0, [])
