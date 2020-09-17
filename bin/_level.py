#!runpy.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pymoab import *
from time import sleep
from signal import signal, SIGINT
from sys import exit, argv
import argparse


def shutdown():
    print("deactivating...")
    lowerPlate()
    sync()
    sleep(0.5)

    # Due to firmware 2.1 bug, disableServoPower sets icon=0 and text=0
    print("cutting servo power")
    disableServoPower()
    sync()
    sleep(0.1)


def setTextIcon(text, icon):
    setText(text)
    setIcon(icon)
    sync()
    sleep(0.1)


def startup():
    # This needs to be called before INIT
    # Also: do not call sync() on this (segfault)
    # print("setting servo offset")
    # setServoOffsets(-2, 1, 0)

    print("initalizing")
    init()
    sync()
    sleep(0.1)

    setTextIcon(Text.INIT, Icon.DOT)

    #print("activating plate")
    #activatePlate()
    #sync()
    #sleep(0.1)


def sigint(signal_received, frame):
    shutdown()
    exit(1)


def main(args):
    startup()

    # min (0) all the way down = 160°
    # max (1) fully-extended = 90°
    # y = 160 - 16x/9
    # 1, 90
    # 0, 160

    x = clamp(args.height, 0, 1)

    y = -70 * x + 160
    print(f"Setting plate to {x:.2f} or {y:.2f}°")

    setServoPositions(y,y,y)
    sync()
    sleep(0.1)
    setTextIcon(Text.CAL_COMPLETE, Icon.DOT)

    print("press menu to quit...")
    sleep(0.1)
    while not getMenuBtn():
        sleep(0.01)
        sync()

    shutdown()


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

def parseArgs():
    p = argparse.ArgumentParser(
        prog="zaxis",
        description="Set the height of the plate in the z-dimension"
    )

    p.add_argument(dest="height",
                   type=float,
                   help="height from 0 to 1")

    if len(argv) == 1:
        p.print_help()
        exit(1)

    args = p.parse_args()
    return args

if __name__ == "__main__":
    args = parseArgs()
    print(vars(args), flush=True)

    signal(SIGINT, sigint)
    main(args)

