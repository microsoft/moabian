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

minRunTime = 5  # seconds
fanIsRunning = False

fan_pin = 26  # HAT fan is BCM 36 (hardware 37) https://pinout.xyz/pinout/pin37_gpio26
pwm_frequency = 7 # max PWM frequency to use. Fan does not seem to run arround 10Hz and above. 
pwm_frequency_factor = 2.5 # pwm_frequency / pwm_frequency_factor = min frequency to use close to 100% duty
min_duty = 50 # below this value the fan turns off
max_duty = 95 # above this value fan turns on fully

def setupGPIO():
    global pwm

    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(fan_pin, gpio.OUT)
    pwm = gpio.PWM(fan_pin, pwm_frequency)
    pwm.start(0) #start PWM off

def turnOff():
    global pwm
    global fanIsRunning
    #gpio.output(fan_pin, gpio.LOW)
    pwm.ChangeDutyCycle(0)
    fanIsRunning = False

def turnOn(duty, temp):
    global pwm
    global fanIsRunning
    #gpio.output(fan_pin, gpio.HIGH)

    if(duty > max_duty):
        duty = 100

    # fan runs faster at lower PWM frequencies
    # dynamically change frequency along with duty
    frequency = pwm_frequency / (1 + (pwm_frequency_factor - 1) * (duty - min_duty) / (100.0 - min_duty))

    if(duty >= min_duty):
        pwm.ChangeDutyCycle(duty)
        pwm.ChangeFrequency(frequency)
        fanIsRunning = True
        #print(f"{temp:.1f}° C; {duty:.1f}%; {frequency:.4f}Hz; FAN: ON", flush=True)
    else:
        turnOff()

def sigint(signal_received, frame):
    global pwm

    turnOff()
    pwm.stop()
    gpio.cleanup()
    exit(1)


def main(args):
    setupGPIO()
    signal(SIGINT, sigint)

    while True:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp = int(file.read()) / 1000.0

            if temp >= args.temperature:
                if fanIsRunning == False:
                    print(f"{temp:.1f}° C; FAN: ON", flush=True)
                duty = (temp - args.temperature) / args.delta * (max_duty - min_duty) + min_duty
                turnOn(duty, temp)

            if temp < (args.temperature) and fanIsRunning == True:
                print(f"{temp:.1f}° C; FAN: OFF", flush=True)
                turnOff()

        time.sleep(args.sec)


def parseArgs():
    p = argparse.ArgumentParser(
        prog="fan",
        description="Manage fan speed as a function of Pi CPU temperature",
        epilog="Ranges: TEMP [40, 60]; DELTA [15, 50]; TEMP + DELTA < 80",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument(
        "-t",
        "--temperature",
        required=False,
        type=int,
        default=55,
        action="store",
        metavar="TEMP",
        help="Fan tuns on above TEMP in degrees Celsius",
    )

    p.add_argument(
        "-d",
        "--delta",
        required=False,
        type=int,
        default=25,
        action="store",
        metavar="DELTA",
        help="Fan will reach max speed at TEMP plus DELTA",
    )

    p.add_argument(
        "-s",
        "--sec",
        required=False,
        type=int,
        default=5,
        action="store",
        metavar="SEC",
        help="Period to poll fan speed and update fan speed setting in seconds",
    )

    args = p.parse_args()
    return args


if __name__ == "__main__":
    args = parseArgs()
    print(vars(args), flush=True)
    
    main(args)
