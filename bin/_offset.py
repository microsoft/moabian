#!runpy.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import sys
import json
import argparse
import textwrap

from pymoab import *
from time import sleep
from signal import signal, SIGINT
from sys import exit, argv


def shutdown():
    sleep(0.01)
    lowerPlate()
    sync()
    sleep(0.5)

    # Due to firmware 2.1 bug, disableServoPower sets icon=0 and text=0
    disableServoPower()
    sync()
    sleep(0.1)


def setTextIcon(text, icon):
    setText(text)
    setIcon(icon)
    sync()
    sleep(0.1)


def startup():
    init()
    sync()
    sleep(0.1)

    setTextIcon(Text.INIT, Icon.DOT)

    activatePlate()
    sync()
    sleep(0.1)


def sigint(signal_received, frame):
    shutdown()
    exit(1)


def set_servo_offsets(s1, s2, s3):
    startup()

    setServoOffsets(s1, s2, s3)
    setPlateAngles(0, 0)
    sync()
    sleep(0.1)
    setTextIcon(Text.CAL_COMPLETE, Icon.DOT)

    print("Press the menu button or CTRL-C to quit...")
    sleep(0.1)
    while not getMenuBtn():
        sleep(0.01)
        sync()

    shutdown()


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


def parse_arguments():
    p = argparse.ArgumentParser(
        prog="offset",
        description="Manage servo offsets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
        Usage:
            offset                  # show current servo offsets
            offset -h               # print usage
            offset -s 5 0 -2        # test a new offset +5, 0, -2
            offset -s 5 0 -2 -w     # save these offsets
        ''')
    )

    p.add_argument("-s", "--servos", required=False, nargs=3,
                   type=int,
                   metavar=("servo1", "servo2", "servo3"))

    p.add_argument(
        "-w",
        "--write",
        required=False,
        action="store_true",
        help="write new offsets to config.json",
    )

    p.add_argument(
        "-f",
        "--file",
        required=False,
        action="store",
        help="optional path to existing calibration.json file",
    )

    args = p.parse_args()
    return args, p


def get_env(key, default):
    if os.environ.get(key) is None:
        return default
    else:
        return os.environ[key]


def get_file_ownership(filename):
    return (os.stat(filename).st_uid, os.stat(filename).st_gid)


def search_for_config(path=None):
    assert path is None or type(path) == str

    # If a --file flag was passed, use that location
    if path:
        return os.path.abspath(args.file)

    # 1. Rely on $MOABDIR if available
    if os.environ.get("MOABDIR"):
        path = os.environ["MOABDIR"] + "/config/calibration.json"
        if os.path.isfile(path):
            return path

    # 2. Test for /app/config/calibration.json (which indicates Docker)
    path = "/app/config/calibration.json"
    if os.path.isfile(path):
        return path

    # 3. Try bare metal
    path = "/home/pi/moab/config/calibration.json"
    if os.path.isfile(path):
        return path

    raise ValueError(f"{path} does not exist")


def print_offsets(filename):
    path = search_for_config(filename)

    if os.path.isfile(path) is False:
        raise ValueError(f"{path} is not a file")

    try:
        print(f"{path}:")
        with open(path, "r") as f:
            data = json.load(f)
            json.dump(data, sys.stdout, indent=2)
    except Exception as e:
        print(f"Failed to read {path}")
        print(e)


def write_offsets(filename, servos):
    path = search_for_config(filename)

    if os.path.isfile(path) is False:
        raise ValueError(f"{path} is not a file")

    # These are the offsets to override
    offsets = {"servoOffsets": servos}

    # First read existing contents...
    try:
        with open(path, "r") as f:
            data = json.load(f)

        with open(path, "w") as f:
            data.update(offsets)
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Failed to write {offsets} to {path}")
        print(e)


if __name__ == "__main__":
    args, parser = parse_arguments()

    signal(SIGINT, sigint)

    if args.write:
        write_offsets(args.file, args.servos)
        print_offsets(args.file)
    elif args.servos:
        set_servo_offsets(*args.servos)
    else:
        print_offsets(args.file)


    exit(0)
