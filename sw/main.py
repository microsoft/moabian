#!/usr/bin/python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Moab Controller

Main entry point for robot runtime stack.

- Actuators: used to make things move
- Sensors: used to pull data from hardware
- Detectors: take sensor output and detect things with it
- Controllers: move actuators based on detected sensor output
- Device: a collection of the above
"""
import argparse
import codecs
import json
import logging as log
import logging.config
import signal
import sys
import time

import pymoab
from dacite import from_dict
from collections import deque
from control.common import IDevice
from control.device import Device
from control.timers import ThreadedTimer, BusyTimer
from control.perfcounters import PerformanceCounters
from control.config import calibration_path, config_path


def printPerformanceCounters():
    PerformanceCounters.logAllCounters()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        default=config_path,
        help="Path to the JSON configuration file to use",
    )
    parser.add_argument(
        "-k",
        "--calibration",
        default=calibration_path,
        help="Path to the JSON configuration file to use",
    )
    parser.add_argument(
        "-d",
        "--device",
        default="menu",
        help="Top level device, usually {menu,calibration,classic}",
    )
    parser.add_argument(
        "-t",
        "--perf-interval-sec",
        default="-1",
        type=int,
        help="Frequency to print perf counters to the 'performance' logger. Values <= 0 suppress this output",
    )

    return parser.parse_args()


def load_config(config_path: str) -> dict:
    config = None
    try:
        with codecs.open(config_path, "r", encoding="utf-8") as fd:
            config = json.load(fd)

        logging.config.dictConfig(config["logging"])

    except Exception as e:
        print(f"Error opening {config_path}\n{e}")
        exit(1)

    return config


warningGiven = False


def load_calibration(calibration_path: str) -> IDevice.Calibration:
    global warningGiven

    calibration: IDevice.Calibration = IDevice.Calibration()
    try:
        with codecs.open(calibration_path, "r", encoding="utf-8") as fd:
            calibration = from_dict(IDevice.Calibration, json.load(fd))
            warningGiven = False
    except Exception as e:
        if warningGiven == False:
            log.warning(f"{calibration_path} not found. CALIBRATE bot.")
            warningGiven = True

    return calibration


def signal_handler(sig, frame) -> int:
    log.info(f"Signal {sig} received, shutting down...")

    # Lower the plate and deactivate the servos
    # lowerPlate is 155º; testing a lower position of 160º
    pymoab.setServoPositions(160, 160, 160)
    pymoab.sync()
    # pymoab.lowerPlate(); pymoab.sync()
    time.sleep(0.2)

    pymoab.disableServoPower()
    pymoab.sync()
    time.sleep(0.1)

    # Clear the screen
    pymoab.setIcon(pymoab.Icon.BLANK)
    pymoab.setText(pymoab.Text.BLANK)
    pymoab.sync()
    time.sleep(0.1)

    sys.exit(0)


def main():
    args = parse_args()

    # load configs
    config = load_config(args.config)

    # Load calibration.json file which contains the ball hue (22 default)
    calibration = load_calibration(args.calibration)

    # Now that log is configured, we can say we're starting up
    log.info("Moab starting.")

    # onetime init of pymoab library
    # side effect of setting OLED to Initalizing... which is ok
    pymoab.init()
    pymoab.sync()
    time.sleep(0.1)

    # put plate in "ready" mode, then cut power until needed
    pymoab.setServoPositions(150, 150, 150)
    pymoab.sync()
    time.sleep(0.1)
    pymoab.disableServoPower()
    pymoab.sync()
    time.sleep(0.1)

    # optional perf timing
    global perf_timer
    if args.perf_interval_sec > 0:
        perf_timer = ThreadedTimer()
        perf_timer.start(args.perf_interval_sec, printPerformanceCounters)

    try:
        devices = config["devices"]
    except Exception as e:
        log.exception(f"Error reading devices from {args.config}\n{e}")
        sys.exit(-1)

    device_stack = deque()
    device_stack.append(args.device)

    previous_menu: int = 0

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:

        curr_device = device_stack.pop() if len(device_stack) > 0 else None
        if curr_device is None:
            break

        try:
            config = from_dict(IDevice.Config, devices.get(curr_device))
            config.menu_idx = previous_menu
            device = Device.createFromConfig(config, calibration)

            log.info("{} §".format(curr_device.upper()))
            device.run()
            previous_menu = device.previous_menu

            # Did our current device ask us to activate another one?
            next_device = device.get_next_device()
            if next_device is not None:
                # Save this device so we can go back to it
                device_stack.append(curr_device)

                # Will be the one popped off next iteration
                device_stack.append(next_device)
        except Exception as e:
            log.exception(f"Error instantiating {args.device}\n{e}")
            curr_device = None
            continue

        # Reload configs
        config = load_config(args.config)
        calibration = load_calibration(args.calibration)


perf_timer = ThreadedTimer()

if __name__ == "__main__":
    main()
