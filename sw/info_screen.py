#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import json
import socket
import logging as log

from env import MoabEnv
from hat import Hat, Icon
from random import randint
from dataclasses import dataclass
from settings import get_settings, set_settings
from typing import Any, Tuple, List


def _get_host_ip():
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 1))
        ip = s.getsockname()[0]  # returns string like '1.2.3.4'
    except Exception as e:
        print(f"No IP: {ip}")

    return ip


def _get_sw_version():
    ver_string = os.environ.get("MOABIAN", "1.0.0")
    ver_triplet = [int(b) for b in ver_string.split(".")]
    log.info(f"Version string: {ver_string}")
    log.info(f"Version triplet: {ver_triplet}")
    return ver_triplet


def info_screen_controller(env, **kwargs):
    sw_major, sw_minor, sw_bug = _get_sw_version()
    ip = _get_host_ip()
    s = f"VER {sw_major}.{sw_minor}.{sw_bug}\nIP {ip}"
    env.hardware.display(s, scrolling=True)

    def wait_for_menu():
        menu_button = False
        while not menu_button:
            time.sleep(1 / env.frequency)
            env.hardware.hat.noop()
            menu_button, joy_button, joy_x, joy_y = env.hardware.hat.get_buttons()

    return wait_for_menu


def info_config_controller(env, **kwargs):
    so = env.hardware.servo_offsets
    s = f"HUE {env.hardware.hue}"
    # s += f"\nX,Y {env.plate_offsets_pixels[0]},{env.plate_offsets_pixels[1]}"
    s += f"\nSERVOS {so[0]:.0f}, {so[1]:.0f}, {so[2]:.0f}"
    env.hardware.display(s, scrolling=True)

    def wait_for_menu():
        menu_button = False
        while not menu_button:
            time.sleep(1 / env.frequency)
            env.hardware.hat.noop()
            menu_button, joy_button, joy_x, joy_y = env.hardware.hat.get_buttons()

    return wait_for_menu


@dataclass
class Option:
    name: str
    value: Any


@dataclass
class SettingsMenuItem:
    name: str
    json_str: str
    options: List[Option]


def matching_menu_option_idx(current_value, options):
    matching_idx = 0  # Top item by default
    for i, opt in enumerate(options):
        if current_value == opt.value:
            matching_idx = i
    return matching_idx


def options_controller(env, **kwargs):
    # TODO: more stable version of this menu
    settings = get_settings()

    inner_menu = [
        SettingsMenuItem(
            "Ball Color",
            "ball_hue",
            [
                Option(f"custom: {settings['ball_hue']}", settings["ball_hue"]),
                Option("orange: 44", 44),
                Option("yellow: 65", 65),
                Option("green: 125", 125),
                Option("blue: 200", 200),
                Option("pink: 325", 325),
            ],
        ),
        SettingsMenuItem(
            "Kiosk",
            "kiosk",
            [
                Option("ON", True),
                Option("OFF", False),
            ],
        ),
        SettingsMenuItem(
            "Kiosk Timeout",
            "kiosk_timeout",
            [
                Option("5", 5),
                Option("10", 10),
                Option("15", 15),
                Option("20", 20),
                Option("30", 30),
                Option("45", 45),
                Option("60", 60),
                Option("90", 90),
            ],
        ),
        SettingsMenuItem(
            "Kiosk Clock Pos",
            "kiosk_clock_position",
            [Option(str(i), i) for i in range(1, 13)],
        ),
    ]

    index_x = 0
    prev_index_x, prev_index_y = -1, -1  # Will update the screen first time
    inner_menu[index_x] = inner_menu[index_x]

    # Get the current value and index of the menu item
    index_y = matching_menu_option_idx(
        current_value=settings[inner_menu[index_x].json_str],
        options=inner_menu[index_x].options,
    )

    def wait_for_menu():
        nonlocal index_x, index_y, prev_index_x, prev_index_y, settings

        menu_button = False
        while not menu_button:

            # Only update screen when state changes
            if prev_index_x != index_x or prev_index_y != index_y:
                s = inner_menu[index_x].name + "\n"
                s += inner_menu[index_x].options[index_y].name
                env.hardware.display(s, scrolling=True)
            else:
                env.hardware.hat.noop()

            time.sleep(1 / env.frequency)
            menu_button, joy_button, joy_x, joy_y = env.hardware.hat.get_buttons()

            # Update prev indices
            prev_index_x, prev_index_y = index_x, index_y

            if joy_x < -0.9:  # Flick joystick left
                prev_index_x = index_x
                index_x = max(0, index_x - 1)
                index_y = matching_menu_option_idx(
                    current_value=settings[inner_menu[index_x].json_str],
                    options=inner_menu[index_x].options,
                )
            elif joy_x > 0.9:  # Flick joystick right
                prev_index_x = index_x
                index_x = min(index_x + 1, len(inner_menu) - 1)
                index_y = matching_menu_option_idx(
                    current_value=settings[inner_menu[index_x].json_str],
                    options=inner_menu[index_x].options,
                )
            elif joy_y < -0.8:  # Flick joystick down
                prev_index_y = index_y
                index_y = min(index_y + 1, len(inner_menu[index_x].options) - 1)
                # Update settings
                menu_opt_json_str = inner_menu[index_x].json_str
                opt_selection_value = inner_menu[index_x].options[index_y].value
                settings[menu_opt_json_str] = opt_selection_value

            elif joy_y > 0.8:  # Flick joystick up
                prev_index_y = index_y
                index_y = max(0, index_y - 1)
                # Update settings
                menu_opt_json_str = inner_menu[index_x].json_str
                opt_selection_value = inner_menu[index_x].options[index_y].value
                settings[menu_opt_json_str] = opt_selection_value

        set_settings(settings)

    return wait_for_menu


def sequence(env, msec=1 / 20):

    info_screen_controller(env)
    for x in range(randint(1, 5)):
        time.sleep(msec)
        env.hardware.hat.noop()

    info_config_controller(env)
    for x in range(randint(1, 15)):
        time.sleep(msec)
        env.hardware.hat.noop()


def main():
    with MoabEnv(debug=True, verbose=3) as env:
        for x in range(10):
            sequence(env)

        env.hardware.display("done")


if __name__ == "__main__":
    main()
