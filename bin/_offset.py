#!runpy.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

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


def main(args):
    startup()

    setServoOffsets(args.servo1, args.servo2, args.servo3)
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

def parseArgs():
    p = argparse.ArgumentParser(
        prog="offset",
        description="Determine servo power offsets"
    )

    p.add_argument(dest="servo1", type=int, help="Integer offset [-5 ... 5]")
    p.add_argument(dest="servo2", type=int, help="Integer offset [-5 ... 5]")
    p.add_argument(dest="servo3", type=int, help="Integer offset [-5 ... 5]")

    if len(argv) != 4:
        p.print_help()
        exit(1)

    args = p.parse_args()
    return args

if __name__ == "__main__":
    args = parseArgs()

    signal(SIGINT, sigint)
    main(args)

