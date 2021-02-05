#!/usr/bin/python3
# vim:filetype=python:

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# You have your orders now, go fan go! -A. Ham

import os
import time
import argparse
import threading as th
import RPi.GPIO as gpio

from sys import exit
from threading import Timer
from datetime import datetime
from signal import signal, SIGINT

setpoint = 60  # fan turns on at this temp
delta = 5  # number of degrees to drop
minRunTime = 5  # seconds
fanIsRunning = False

fan_pin = 26  # HAT fan is BCM 36 (hardware 37) https://pinout.xyz/pinout/pin37_gpio26


def setupGPIO():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(fan_pin, gpio.OUT)


def turnOn():
    global fanIsRunning
    gpio.output(fan_pin, gpio.HIGH)
    fanIsRunning = True


def turnOff():
    global fanIsRunning
    gpio.output(fan_pin, gpio.LOW)
    fanIsRunning = False


def sigint(signal_received, frame):
    turnOff()
    gpio.cleanup()
    exit(1)


def main(args):
    setupGPIO()
    signal(SIGINT, sigint)

    while True:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp = int(file.read()) / 1000.0

            if temp >= args.temperature and fanIsRunning == False:
                print(f"{temp:.1f}° C; FAN: ON", flush=True)
                turnOn()

            if temp < (args.temperature - args.delta) and fanIsRunning == True:
                print(f"{temp:.1f}° C; FAN: OFF", flush=True)
                turnOff()

        time.sleep(args.sec)


def parseArgs():
    p = argparse.ArgumentParser(
        prog="fan",
        description="Turn on the fan when the CPU hits this temperature",
        epilog="Ranges: TEMP [40, 80]; DELTA [0, 10]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument(
        "-t",
        "--temperature",
        required=False,
        type=int,
        default=60,
        action="store",
        metavar="TEMP",
        help="setpoint in degrees Celsius",
    )

    p.add_argument(
        "-d",
        "--delta",
        required=False,
        type=int,
        default=5,
        action="store",
        metavar="DELTA",
        help="turn off fan at TEMP minus DELTA",
    )

    p.add_argument(
        "-s",
        "--sec",
        required=False,
        type=int,
        default=5,
        action="store",
        metavar="SEC",
        help="minimum run time for fan in seconds",
    )

    args = p.parse_args()
    return args


if __name__ == "__main__":
    args = parseArgs()
    print(vars(args), flush=True)

    main(args)
