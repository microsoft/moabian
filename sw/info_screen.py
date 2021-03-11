#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import socket
import logging as log
from hat import Hat
from env import MoabEnv

def _get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 1))
    ip = s.getsockname()[0]  # returns string like '1.2.3.4'
    ip_quads = [int(b) for b in ip.split(".")]
    log.info(f"IP: {ip}")
    return ip_quads

def _get_sw_version():
    ver_string = os.environ.get("MOABIAN", "1.0.0")
    ver_triplet = [int(b) for b in ver_string.split(".")]
    log.info(f"Version string: {ver_string}")
    log.info(f"Version triplet: {ver_triplet}")
    return ver_triplet

def get_info_string():
    return s

def info_screen_controller(env=None, **kwargs):
    sw_major, sw_minor, sw_bug = _get_sw_version()
    ip1, ip2, ip3, ip4 = _get_host_ip()
    s = f"VER: {sw_major}.{sw_minor}.{sw_bug}\nIP : {ip1}.{ip2}.{ip3}.{ip4}"

    env.hat.display_long_string(s)
    return lambda state: ((0, 0), {})

def info_config_controller(env=None, **kwargs):
    s = f"HUE: {env.hue}\n"
    s += f"BIAS: {env.servo_offsets}"

    env.hat.display_long_string(s)
    return lambda state: ((0, 0), {})

def main():
    with MoabEnv(debug=True) as env:
        print(env)

        info_screen_controller(env)
        input("Press ENTER to quit")

        info_config_controller(env)
        input("Press ENTER to quit")
        env.hat.display_string("done")

if __name__ == "__main__":  # Parse command line args
    main()
