# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import socket
import spidev
import numpy as np
import logging as log
import RPi.GPIO as gpio

from hexyl import hexyl
from enum import IntEnum
from common import Buttons
from typing import Union, List, Tuple

# fmt: off
# Define which bytes represent which commands

# Messaging from the Pi to the hat
class SendCommand(IntEnum):
    NOOP                    = 0x00
    SERVO_ENABLE            = 0x01  # The servos should be turned off
    SERVO_DISABLE           = 0x02  # The servos should be turned on
    SET_PLATE_ANGLES        = 0x04  # Set the plate angles (pitch and roll)
    SET_SERVOS              = 0x05  # Set the servo positions manually (s1, s2, s3)
    COPY_STRING             = 0x80  # There is a arbitrary length string being transmitted (max len 240 bytes) and copy into the text buffer
    DISPLAY_BIG_TEXT_ICON   = 0x81  # Display what is currently in the buffer (large font) along with an icon sent in this message. Does not scroll.
    DISPLAY_BIG_TEXT        = 0x82  # Display only what is currently in the buffer (large font). Does not scroll.
    DISPLAY_SMALL_TEXT_SCROLLING = 0x83  # Display only what is currently in the buffer (small font). Scroll if required.

class Text(IntEnum):
    BLANK = 0
    INIT = 1
    POWER_OFF = 2
    ERROR = 3
    CAL = 4
    MANUAL = 5
    CLASSIC = 6
    BRAIN = 7
    CUSTOM1 = 8
    CUSTOM2 = 9
    INFO = 10
    CAL_INSTR = 11
    CAL_COMPLETE = 12
    CAL_CANCELED = 13
    CAL_FAILED = 14
    VERS_IP_SN = 15
    UPDATE_BRAIN = 16
    UPDATE_SYSTEM = 17

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
    return b if b < 128 else (-256 + b)


def _int8_to_uint8(b: int) -> int:
    """
    Converts a byte to a signed int (int8) instead of unsigned int (uint8).
    """
    return np.uint8(b)  # b if b > 0 else (256 - b)


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


def plate_angles_to_servo_positions(
    theta_x: float,
    theta_y: float,
    arm_len: float = 55.0,
    side_len: float = 170.87,
    pivot_height: float = 80.0,
    angle_max: float = 160,
    angle_min: float = 90,
) -> Tuple[float, float, float]:
    servo_angles = [0.0, 0.0, 0.0]

    z1 = pivot_height + np.sin(np.radians(-theta_y)) * (side_len / np.sqrt(3))
    r = pivot_height - np.sin(np.radians(-theta_y)) * (side_len / (2 * np.sqrt(3)))
    z2 = r + np.sin(np.radians(theta_x)) * (side_len / 2)
    z3 = r - np.sin(np.radians(theta_x)) * (side_len / 2)

    if z1 > 2 * arm_len:
        z1 = 2 * arm_len
    if z2 > 2 * arm_len:
        z2 = 2 * arm_len
    if z3 > 2 * arm_len:
        z3 = 2 * arm_len

    servo_angles[0] = 180 - (np.degrees(np.arcsin(z1 / (2 * arm_len))))
    servo_angles[1] = 180 - (np.degrees(np.arcsin(z2 / (2 * arm_len))))
    servo_angles[2] = 180 - (np.degrees(np.arcsin(z3 / (2 * arm_len))))

    servo_angles = np.clip(servo_angles, angle_min, angle_max)
    return servo_angles


# Return an exact 8 byte numpy array
def pad(*args, **kwargs):
    data = [*args][:8]
    pads = (8 - len(data)) * [0]
    dtype = kwargs.pop("dtype", np.int8)
    return np.array(data + pads, dtype)


class Hat:
    def __init__(
        self,
        servo_offsets: Tuple[float, float, float] = (0, 0, 0),
        use_plate_angles=False,
        use_hexyl=False,
    ):
        self.servo_offsets: Tuple[float, float, float] = servo_offsets
        self.buttons = Buttons(False, False, 0.0, 0.0)
        self.last_icon = -1
        self.last_text = -1

        self.use_plate_angles = use_plate_angles
        self.use_hexyl = use_hexyl
        if use_hexyl:
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
            time.sleep(1.0)
        except KeyboardInterrupt:
            raise
        except:
            raise IOError(f"Could not setup GPIO pins")

    def close(self, text="OFF"):
        self.display_string(text)
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

        if self.use_hexyl:
            self.hex_printer(packet.tolist(), hat_to_pi)

        # Check if buttons are pressed
        self.buttons.menu_button = hat_to_pi[0] == 1
        self.buttons.joy_button = hat_to_pi[1] == 1

        # Get x & y coordinates of joystick normalized to [-1, +1]
        self.buttons.joy_x = _uint8_to_int8(hat_to_pi[2]) / 100
        self.buttons.joy_y = _uint8_to_int8(hat_to_pi[3]) / 100

    def get_buttons(self) -> Tuple[bool, bool, float, float]:
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
        """ Set the plate to track plate angles. """
        self.transceive(pad(SendCommand.SERVO_ENABLE))

    def disable_servos(self):
        """ Disables the power to the servos. """
        self.transceive(pad(SendCommand.SERVO_DISABLE))

    def set_angles(self, plate_x: float, plate_y: float):
        # If set_plate_angles flag is set, use the plate to servo conversion on
        # the hat, otherwise use the one in Python

        if self.use_plate_angles:
            # Take into account offsets when converting from degrees to values sent to hat
            plate_x, plate_y = _xy_offsets(plate_x, plate_y, self.servo_offsets)
            plate_x, plate_y = -plate_x, -plate_y
            self.transceive(pad(SendCommand.SET_PLATE_ANGLES, plate_x, plate_y))

        else:
            s1, s2, s3 = plate_angles_to_servo_positions(-plate_x, -plate_y)
            s1 += self.servo_offsets[0]
            s2 += self.servo_offsets[1]
            s3 += self.servo_offsets[2]
            self.set_servos(s1, s2, s3)

    def set_servos(self, servo1: float, servo2: float, servo3: float):
        # Note the off by 1 for indexing
        servo1 += self.servo_offsets[0]
        servo2 += self.servo_offsets[1]
        servo3 += self.servo_offsets[2]

        # Use fixed point 16-bit numbers, with precision of hundredths
        servo1_centi_degrees = np.int16(servo1 * 100)
        servo2_centi_degrees = np.int16(servo2 * 100)
        servo3_centi_degrees = np.int16(servo3 * 100)

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

    def set_servo_offsets(self, servo1: int, servo2: int, servo3: int):
        """
        Set post-factory calibration offsets for each servo.
        Normally this call should not be needed.
        """
        self.servo_offsets = (servo1, servo2, servo3)

    def hover(self):
        """
        Set the plate to its hover position.
        This was experimentally found to be 150 (down but still leaving some
        space at the bottom).
        """
        self.set_servos(150, 150, 150)
        # Give enough time for the action to be taken
        time.sleep(0.200)  # Make sure this action gets taken before turning off servos

    def lower(self):
        """
        Set the plate to its lower position (usually powered-off state).
        This was experimentally found to be 155 (lowest possible position).
        """
        self.set_servos(155, 155, 155)
        # Give enough time for the action to be taken
        time.sleep(0.200)  # Make sure this action gets taken before turning off servos

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

            # TODO: Why is this sleep here instead of before display command?
            time.sleep(0.090)

    def set_icon_text(self, icon_idx: Icon, text_idx: Text):
        texts = {
            0: ("BLANK", True),
            1: ("INITIALIZING", False),
            2: ("POWER_OFF", False),
            3: ("ERROR", True),
            4: ("CALIBRATE", True),
            5: ("JOYSTICK", True),
            6: ("PID", True),
            7: ("BRAIN", True),
            8: ("CUSTOM 1", True),
            9: ("CUSTOM 2", True),
            10: ("BOT INFO", True),
            12: ("CAL_COMPLETE", True),
            13: ("CALIBRATION\nCANCELED", False),
            14: ("FAILED", False),
        }
        text = texts[text_idx][0]
        uses_icon = texts[text_idx][1]
        if uses_icon:
            self.display_string_icon(text, icon_idx)
        else:
            self.display_string(text)

    def display_string_icon(self, text: str, icon_idx: Icon):
        assert len(text) <= 12, "String is too long to diplay with icon"

        # Don't needlessly update display if text AND icon haven't changed
        if text == self.last_text and icon_idx == self.last_icon:
            return

        self.last_text = text
        self.last_icon = icon_idx

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a long string
        self.transceive(pad(SendCommand.DISPLAY_BIG_TEXT_ICON, icon_idx))

    def display_string(self, text: str):
        assert len(text) <= 15, "String is too long to diplay without scrolling."

        # Don't needlessly update display if text haven't changed (and there was no prev icon)
        if text == self.last_text and icon_idx == self.last_icon:
            return

        self.last_text = text
        self.last_icon = -1  # This means the last icon was no icon

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a long string
        self.transceive(pad(SendCommand.DISPLAY_BIG_TEXT))


    def display_long_string(self, text: str):
        # reset the text/icon index optimization hack
        self.last_text = -1
        self.last_icon = -1  # This means the last icon was no icon

        # Copy the text into a buffer in the firmware
        self._copy_buffer(text)

        # After sending copying to the fw buffer, display the buffer as a long string
        self.transceive(pad(SendCommand.DISPLAY_SMALL_TEXT_SCROLLING))


    def print_info_screen(self):
        sw_major, sw_minor, sw_bug = _get_sw_version()
        ip1, ip2, ip3, ip4 = _get_host_ip()
        self.display_long_string(
            f"VER: {sw_major}.{sw_minor}.{sw_bug}\n"
            f"IP : {ip1}.{ip2}.{ip3}.{ip4}\n"
        )
