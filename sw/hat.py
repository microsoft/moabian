# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import signal

import socket
import spidev
import numpy as np
import logging as log
import RPi.GPIO as gpio

from hexyl import hexyl
from enum import IntEnum
from dataclasses import dataclass, astuple
from typing import Union, List, Tuple, Optional

# fmt: off
# Define which bytes represent which commands

# Messaging from the Pi to the hat
class SendCommand(IntEnum):
    NOOP                    = 0x00  # Import for polling the state of the buttons and joystick
    SERVO_ENABLE            = 0x01  # The servos should be turned off
    SERVO_DISABLE           = 0x02  # The servos should be turned on
    SET_SERVOS              = 0x05  # Set the servo positions manually (s1, s2, s3)
    COPY_STRING             = 0x80  # Pass a variable length string (max 240 bytes). Requires DISPLAY_ after.
    DISPLAY_BIG_TEXT_ICON   = 0x81  # Display buffer (large font) with icon. Does not scroll.
    DISPLAY_BIG_TEXT        = 0x82  # Display the 0x80 buffer (in large font). Does not scroll.
    DISPLAY_SMALL_TEXT      = 0x83  # Display the 0x80 buffer (in small font). Scroll if required.
    DISPLAY_POWER_SYMBOL    = 0x84  # Display buffer (large font) with icon. Does not scroll.

# Icon index
class Icon(IntEnum):
    BLANK = 0
    UP_DOWN = 1
    DOWN = 2
    UP = 3
    DOT = 4
    PAUSE = 5
    CHECK = 6
    X = 7

# ⏻ ⏼ ⏽ ⭘ ⏾
class PowerIcon(IntEnum):
    POWER = 1
    TOGGLE_POWER = 2
    POWER_ON = 3
    SLEEP_MODE = 4
    POWER_OFF = 5


@dataclass
class Buttons:
    menu_button: bool = False
    joy_button: bool = False
    joy_x: float = 0.0
    joy_y: float = 0.0

    def __iter__(self):
        return iter(astuple(self))


# GPIO pins
class GpioPin(IntEnum):
    HAT_EN    = 20  # Bcm 20 - RPi pin 38 - RPI_BPLUS_GPIO_J8_38
    HAT_RESET = 6   # Bcm 6  - RPi pin 31 - RPI_BPLUS_GPIO_J8_31
# fmt: on


# Helper functions -------------------------------------------------------------
def _uint8_to_int8(b: int) -> int:
    """
    Converts a byte to a signed int (int8) instead of unsigned int (uint8).
    """
    return np.int8(b)


def _int8_to_uint8(b: int) -> int:
    """
    Converts a byte to a signed int (int8) instead of unsigned int (uint8).
    """
    return np.uint8(b)


def _xy_offsets(
    x: float,
    y: float,
    servo_offsets: Tuple[float, float, float],
    x_tilt_servo1: float = -0.5,
    y_tilt_servo2: float = 0.866,
    y_tilt_servo3: float = -0.866,
) -> Tuple[float, float]:
    so_1, so_2, so_3 = servo_offsets
    x_offset = x + so_1 + x_tilt_servo1 * so_2 + x_tilt_servo1 * so_3
    y_offset = y + y_tilt_servo2 * so_2 + y_tilt_servo3 * so_3
    return x_offset, y_offset


# Return an exact 8 byte numpy array
def pad(*args, **kwargs):
    data = [*args][:8]
    pads = (8 - len(data)) * [0]
    dtype = kwargs.pop("dtype", np.int8)
    return np.array(data + pads, dtype)


class Hat:
    """
    A helper class that solely does SPI messages. It contains some state for the
    SPI connection, GPIO pins, and saves responses from the hat. Nothing at a
    higher level of abstraction should be done here.
    """

    def __init__(
        self,
        debug=False,
        verbose=0,
    ):
        self.buttons = Buttons(False, False, 0.0, 0.0)
        self.debug = debug
        self.verbose = verbose
        if debug:
            self.hex_printer = hexyl()
        self.spi = None

    def open(self):
        # Attempt to open the spidev bus
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 100000
        except Exception as e:
            # possible that ctrl-C was caught here
            raise IOError(f"Could not open `/dev/spidev{spi_bus}.{spi_device}`.")

        # Attempt to setup the GPIO pins
        try:
            gpio.setwarnings(False)
            gpio.setmode(gpio.BCM)
            # Setting pin direction, in our case, reboots Moab!
            gpio.setup(
                [GpioPin.HAT_EN, GpioPin.HAT_RESET],
                gpio.OUT,
            )
            time.sleep(0.1)
        except KeyboardInterrupt:
            raise
        except:
            raise IOError(f"Could not setup GPIO pins")

    def close(self):
        if self.spi is not None:
            self.spi.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def transceive(self, packet: np.ndarray):
        """
        Send and receive 8 bytes from hat.
        """
        assert self.spi is not None  # did you call hat.open() first ?
        assert len(packet) == 8

        hat_to_pi = self.spi.xfer(packet.tolist())
        time.sleep(0.005)

        if self.debug:
            self.hex_printer(packet.tolist(), hat_to_pi, self.verbose)

        # Check if buttons are pressed
        self.buttons.menu_button = hat_to_pi[0] == 1
        self.buttons.joy_button = hat_to_pi[1] == 1

        # Get x & y coordinates of joystick normalized to [-1, +1]
        self.buttons.joy_x = _uint8_to_int8(hat_to_pi[2]) / 100
        self.buttons.joy_y = _uint8_to_int8(hat_to_pi[3]) / 100

    def get_buttons(self) -> Buttons:
        """
        Check whether buttons are pressed and the joystick x & y values in the
        response.

        Return:
            Buttons
            Which is a dataclass with:
                - menu_button: bool
                - joy_button : bool
                - joy_x   : float normalized from -1 to +1
                - joy_y   : float normalized from -1 to +1
        """
        return self.buttons

    def noop(self):
        """Send a NOOP. Useful for if you just want to read buttons."""
        self.transceive(pad(SendCommand.NOOP))

    def enable_servos(self):
        """Set the plate to track plate angles."""
        self.transceive(pad(SendCommand.SERVO_ENABLE))

    def disable_servos(self):
        """Disables the power to the servos."""
        self.transceive(pad(SendCommand.SERVO_DISABLE))

    def set_servos(
        self,
        servos: Tuple[float, float, float],
    ):
        # Note the off by 1 for indexing
        # Use fixed point 16-bit numbers, with precision of hundredths
        servo1_centi_degrees = np.int16(servos[0] * 100)
        servo2_centi_degrees = np.int16(servos[1] * 100)
        servo3_centi_degrees = np.int16(servos[2] * 100)

        # Get the first 8 bits and last 8 bits of every 16-bit integer
        # (To send it as indivdual bytes)
        servo1_centi_degrees_high_byte = servo1_centi_degrees >> 8
        servo1_centi_degrees_low_byte = servo1_centi_degrees & 0x00FF
        servo2_centi_degrees_high_byte = servo2_centi_degrees >> 8
        servo2_centi_degrees_low_byte = servo2_centi_degrees & 0x00FF
        servo3_centi_degrees_high_byte = servo3_centi_degrees >> 8
        servo3_centi_degrees_low_byte = servo3_centi_degrees & 0x00FF

        self.transceive(
            pad(
                SendCommand.SET_SERVOS,
                servo3_centi_degrees_high_byte,
                servo3_centi_degrees_low_byte,
                servo1_centi_degrees_high_byte,
                servo1_centi_degrees_low_byte,
                servo2_centi_degrees_high_byte,
                servo2_centi_degrees_low_byte,
            )
        )

    def _copy_buffer(self, s: str):
        s = s.upper()  # The firware currently only has uppercase fonts

        s = bytes(s, "utf-8")
        s += b"\0"  # Ensure a trailing termination character
        assert len(s) <= 240, "String too long to send to hat."

        # Calculate the number of messages required to send the text
        num_msgs = int(np.ceil(len(s) / 7))

        # Pad the message with trailing termination chars to so we always
        # send in 8 bytes increments (1 byte control, 7 bytes data)
        s += (num_msgs * 7 - len(s)) * b"\0"

        for msg_idx in range(num_msgs):
            # Combine into one list to send
            msg = [SendCommand.COPY_STRING] + list(s[7 * msg_idx : 7 * msg_idx + 7])
            self.transceive(np.array(msg, dtype=np.int8))
            time.sleep(0.010)

    def display_power_symbol(self, text: str, icon_idx: PowerIcon):
        assert len(text) <= 12, "String is too long to display with icon"

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a short string
        self.transceive(pad(SendCommand.DISPLAY_POWER_SYMBOL, icon_idx))

    def display_string_icon(self, text: str, icon_idx: Icon):
        # assert len(text) <= 12, "String is too long to display with icon"

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a short string
        self.transceive(pad(SendCommand.DISPLAY_BIG_TEXT_ICON, icon_idx))

    def update_icon(self, icon_idx: Icon):
        # Don't needlessly update display if icon hasn't changed or if last text
        # didn't have an icon (ie last called send text was display_string or
        # display_long_string)

        # Display the buffer as a long string
        self.transceive(pad(SendCommand.DISPLAY_BIG_TEXT_ICON, icon_idx))

    def display_string(self, text: str):
        assert len(text) <= 15, "String is too long to display without scrolling."

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a short string
        self.transceive(pad(SendCommand.DISPLAY_BIG_TEXT))

    def display_long_string(self, text: str):
        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a long string
        self.transceive(pad(SendCommand.DISPLAY_SMALL_TEXT))
