import RPi.GPIO as GPIO
import subprocess
import time
import os

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is BCM pin 3; (hardware pin 5)
# https://pinout.xyz/pinout/pin5_gpio3
POWER_BUTTON = 3

# Pin 3 is setup in /boot/config.txt to be active when it's low (0)
# So when it's unpressed, or "off" it's in a high state (1)
POWER_BUTTON_ON = 0
POWER_BUTTON_OFF = 1
SLEEPTIME = 0.1

# State that determines whether docker run loop is running
MOABRUNLOOP_OFF = 0
MOABRUNLOOP_RUNNING = 1


def check_moab_run():
    output = subprocess.run(["docker-compose ps | grep Up"], shell=True)
    print("docker-compose is running: ", output.returncode == MOABRUNLOOP_RUNNING)
    if output.returncode == 1:  # Not running
        return MOABRUNLOOP_OFF
    elif output.returncode == 0:  # Running
        return MOABRUNLOOP_RUNNING
    else:
        raise ValueError("Could not determine if docker-compose is running")


def shutdown():
    print("SYSTEM SHUTDOWN")
    # Clean up resources before shutting down
    GPIO.cleanup()
    output = subprocess.run(["sudo", "shutdown", "now"], text=True)


def dc_up():
    print("Button TAP, running `docker-compose up`")
    # Use Popen as a non-blocking call
    output = subprocess.Popen(["docker-compose", "up"], text=True)


def dc_down():
    print("Button TAP, running `docker-compose down`")
    # Use Popen as a non-blocking call
    output = subprocess.Popen(["docker-compose", "down"], text=True)


def main():
    # Change working directory to ~/moab (so that the docker-compose commands work)
    os.chdir("/home/pi/moab")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    button_press_count = 0
    state = check_moab_run()

    while True:
        pressed = GPIO.input(POWER_BUTTON)

        # If power button has already been held for longer than 3 seconds: SHUTDOWN
        if button_press_count >= (3 / SLEEPTIME):
            button_press_count = 0
            shutdown()
        # Button was tapped (held for less than 3 seconds and let go)
        elif button_press_count > 0 and pressed == POWER_BUTTON_OFF:
            if state == MOABRUNLOOP_RUNNING:
                dc_down()
                state = MOABRUNLOOP_OFF  # Docker run loop is now off
            else:
                dc_up()
                state = MOABRUNLOOP_RUNNING
            button_press_count = 0
        elif pressed == POWER_BUTTON_ON:
            button_press_count += 1

        time.sleep(SLEEPTIME)


if __name__ == "__main__":
    main()
