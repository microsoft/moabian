#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from random import *
from time import *
import socket
import logging as log
from hat import Hat, Icon
from env import MoabEnv


def _get_host_ip():
    ip = '127.0.0.1'
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
    env.hat.display_long_string(s)

    def wait_for_menu():
        menu_button = False
        while not menu_button:
            sleep(1 / env.frequency)
            env.hat.noop()
            menu_button, joy_button, joy_x, joy_y = env.hat.get_buttons()

    return wait_for_menu


def info_config_controller(env, **kwargs):
    so = ",".join(map(str, env.servo_offsets))
    s = f"HUE {env.hue}"
    s += f"\nX,Y {env.plate_offsets_pixels[0]},{env.plate_offsets_pixels[1]}"
    # s += f"\nSO {so}"
    env.hat.display_long_string(s)

    def wait_for_menu():
        menu_button = False
        while not menu_button:
            sleep(1 / env.frequency)
            env.hat.noop()
            menu_button, joy_button, joy_x, joy_y = env.hat.get_buttons()

    return wait_for_menu


def sequence(env, msec=1 / 20):

    info_screen_controller(env)
    for x in range(randint(1, 5)):
        sleep(msec)
        env.hat.noop()

    info_config_controller(env)
    for x in range(randint(1, 15)):
        sleep(msec)
        env.hat.noop()


def main():
    with MoabEnv(debug=True, verbose=3) as env:
        for x in range(10):
            sequence(env)

        env.hat.display_string("done")


if __name__ == "__main__":
    main()
