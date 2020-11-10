#!foo.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import sys
import json

from pymoab import *
from time import sleep
from signal import signal, SIGINT
from sys import exit, argv
import argparse


def shutdown():
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
        description="Determine servo power offsets"
    )

    p.add_argument(dest="servo1", type=int, help="Integer offset [-5 ... 5]")
    p.add_argument(dest="servo2", type=int, help="Integer offset [-5 ... 5]")
    p.add_argument(dest="servo3", type=int, help="Integer offset [-5 ... 5]")

    p.add_argument("-i", "--ignore", required=False, action="store_true")

    p.add_argument("-s", "--save",
                   required=False,
                   action="store_true",
                   help="save settings to config.json")

    p.add_argument("-f", "--file",
                   required=False,
                   action="store",
                   help="optional path to existing calibration.json file")

    args = p.parse_args()
    return args


def get_env(key, default):
    if os.environ.get(key) is None:
        return default
    else:
        return os.environ[key]


def get_file_ownership(filename):
    return (
        os.stat(filename).st_uid,
        os.stat(filename).st_gid
    )


def search_for_config():
    # Heuristic to find config file

    # 1. Rely on $MOABDIR if available
    if os.environ.get("MOABDIR") is not None:
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

    return None

def save_configuration(args):
    if args.file is not None:
        path = os.path.abspath(args.file)
    else:
        path = search_for_config()

    if path is None:
        print("Unable to find calibration.json file: use --file to specify", file=sys.stderr)
        exit(-1)

    if os.path.isfile(path) is False:
        print(f"{path} is not a file", file=sys.stderr)
        exit(-1)

    # These are the offsets to override
    offsets = { "servoOffsets": [args.servo1, args.servo2, args.servo3] }

    # First read existing contents...
    try:
        print(f"path:{path}")
        with open(path, 'r') as f:
            data = json.load(f)

        with open(path, 'w') as f:
            data.update(offsets)
            json.dump(data, f, indent = 2)

    except Exception as e:
        print(f"Failed to write {offsets} to {path}")
        print(e)


def tween(s1, s2, s3):
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

def hover():
    path = search_for_config()

    print(f"path:{path}")
    offsets = []

    with open(path, 'r') as f:
        data = json.load(f)
        offsets = data['servoOffsets']

    print(offsets)
    tween(*offsets)


if __name__ == "__main__":
    args = parse_arguments()

    signal(SIGINT, sigint)

    if args.ignore:
        hover()
    elif args.save:
        save_configuration(args)
    else:
        set_servo_offsets(args.servo1, args.servo2, args.servo3)

    exit(0)

