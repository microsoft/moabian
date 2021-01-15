# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Menu Controller

Use joystick to navigate between other controllers.
"""

from typing import ClassVar, List
from dataclasses import dataclass, field
from control.hat import interface as pymoab

from ..common import IController, IDevice


@dataclass
class MenuItem:
    icon: str = ""
    text: str = ""
    device: str = ""
    icon2: str = ""


class MenuController(IController):
    @dataclass
    class Config(IController.Config):
        menuItems: List[MenuItem] = field(
            default_factory=lambda: [
                MenuItem("DOWN", "MANUAL", "manual", "DOT"),
                MenuItem("UP_DOWN", "CLASSIC", "classic", "DOT"),
                MenuItem("UP_DOWN", "BRAIN", "brain", "DOT"),
                MenuItem("UP_DOWN", "CUSTOM1", "custom1", "DOT"),
                MenuItem("UP_DOWN", "CUSTOM2", "custom2", "DOT"),
                MenuItem("UP_DOWN", "CAL", "calibration", "BLANK"),
                MenuItem("UP", "INFO", "info", "BLANK"),
            ]
        )

    def __init__(self, config: Config, device: IDevice):
        super().__init__(config, device)
        self.config = config

        self.menu_items = self.config.menuItems
        self.menu_idx = device.previous_menu

        self.display_menu_item(self.menu_idx)

    def display_menu_item(self, idx: int):
        pymoab.set_icon_text(
            pymoab.Icon[self.menu_items[idx].icon],
            pymoab.Text[self.menu_items[idx].text],
        )

    def on_flick_down(self, sender: IDevice):
        self.menu_idx = min(len(self.menu_items) - 1, self.menu_idx + 1)
        self.display_menu_item(self.menu_idx)

    def on_flick_up(self, sender: IDevice):
        self.menu_idx = max(0, self.menu_idx - 1)
        self.display_menu_item(self.menu_idx)

    def on_joy_down(self, sender: IDevice):
        menu_item = self.menu_items[self.menu_idx]
        sender.set_next_device(menu_item.device)
        pymoab.set_icon_text(pymoab.Icon[menu_item.icon2], pymoab.Text[menu_item.text])

        # save the menu item so we pop back up to this index when we return
        sender.previous_menu = self.menu_idx

        sender.stop()
