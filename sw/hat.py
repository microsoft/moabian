# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import os
import time
import socket
import spidev
import numpy as np
import logging as log
import RPi.GPIO as gpio

from enum import IntEnum
from typing import Union, List, Tuple


# fmt: off
# Define which bytes represent which commands

# Messaging from the Pi to the hat
class SendCommand(IntEnum):
    NOOP                    = 0x00
    SERVO_ENABLE            = 0x01  # The servos should be turned off
    SERVO_DISABLE           = 0x02  # The servos should be turned on
    CONTROL_INFO            = 0x03  # This packet contains control info
    SET_PLATE_ANGLES        = 0x04  # Set the plate angles (x and y angles)
    SET_SERVOS              = 0x05  # Set the servo positions manually
    TEXT_ICON_SELECT        = 0x06  # This packet contains the text and icon to be selected and displays both
    DISPLAY_BUFFER          = 0x07  # The LED screen displays what is currently in the buffer
    SET_DEBUGGING_OFF       = 0x40  # (Log level 0) Print nothing
    SET_DEBUGGING_EMERG     = 0x40  # (Log level 0) Print only emergencies
    SET_DEBUGGING_ALERT     = 0x41  # (Log level 1) Print only actions that must be taken immediately and above
    SET_DEBUGGING_CRIT      = 0x42  # (Log level 2) Print only critical conditions and above
    SET_DEBUGGING_ERR       = 0x43  # (Log level 3) Print only errors and above
    SET_DEBUGGING_WARNING   = 0x44  # (Log level 4) Print warnings and above
    SET_DEBUGGING_NOTICE    = 0x45  # (Log level 5) Print notices and above
    SET_DEBUGGING_INFO      = 0x46  # (Log level 6) Print info and above
    SET_DEBUGGING_DEBUG     = 0x47  # (Log level 7) Print everything possible
    REQUEST_STATE_INFO      = 0x4E  # Return the state info (all the information in the main loop of the firmware)
    REQUEST_FW_VERSION      = 0x4F  # Ask the hat to reply back the firmware version, fw version < 2.5 will not reply
    ARBITRARY_MESSAGE       = 0x80  # There is a arbitrary length message being transmitted (max len 256 bytes)
                                    # and put into the text buffer

# Messaging from the hat to the Pi
class ReceiveCommand(IntEnum):
    REPLY_NORMAL            = 0x01  # Normal operation, send back buttons & joystick values
    REPLY_FW_VERSION        = 0x02  # Respond with the firmware version


class Icon(IntEnum):
    BLANK = 0
    UP_DOWN = 1
    DOWN = 2
    UP = 3
    DOT = 4
    PAUSE = 5
    CHECK = 6
    X = 7


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


class Button(IntEnum):
    MENU = 1
    JOYSTICK = 2


class JoystickByteIndex(IntEnum):
    X = 1
    Y = 2


# GPIO pins
class GpioPin(IntEnum):
    BOOT_EN   = 5   # Bcm 5  - RPi pin 29 - RPI_BPLUS_GPIO_J8_29
    HAT_EN    = 20  # Bcm 20 - RPi pin 38 - RPI_BPLUS_GPIO_J8_38
    HAT_RESET = 6   # Bcm 6  - RPi pin 31 - RPI_BPLUS_GPIO_J8_31
    HAT_PWR_N = 3   # Bcm 3  - RPi pin 5  - RPI_BPLUS_GPIO_J8_05


X_TILT_SERVO1 = -0.5
Y_TILT_SERVO2 = 0.866
Y_TILT_SERVO3 = -0.866
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


def setupGPIO():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(
        [GpioPin.BOOT_EN, GpioPin.HAT_EN, GpioPin.HAT_RESET],
        gpio.OUT,
    )
    gpio.setup(GpioPin.HAT_PWR_N, gpio.IN)


def runtime():
    """ Set mode to runtime mode (not bootloader mode). """
    gpio.output(GpioPin.HAT_EN, gpio.LOW)
    time.sleep(0.02)  # 20ms
    gpio.output(GpioPin.HAT_EN, gpio.HIGH)
    gpio.output(GpioPin.HAT_RESET, gpio.LOW)
    gpio.output(GpioPin.BOOT_EN, gpio.LOW)
    time.sleep(0.25)  # 250ms


def _xy_offsets(x, y, servo_offsets: Tuple[float, float, float]) -> Tuple[float, float]:
    so_1, so_2, so_3 = servo_offsets

    x_offset = x + so_1 + X_TILT_SERVO1 * so_2 + X_TILT_SERVO1 * so_3
    y_offset = y + Y_TILT_SERVO2 * so_2 + Y_TILT_SERVO3 * so_3
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


def right_pad_array(arr: Union[List, np.ndarray], length, dtype) -> np.ndarray:
    len_arr = len(arr)
    if len_arr < 9:
        padded_arr = np.zeros(length, dtype=dtype)
        padded_arr[:len_arr] = arr
        return padded_arr
    elif len_arr == 9:
        return np.asarray(arr)
    else:
        raise ValueError(f"Given array: `{arr}` is longer than padded len: {length}.")


class Hat:
    def __init__(
        self,
        spi_bus: int = 0,
        spi_device: int = 0,
        spi_max_speed_hz: int = 10000,
        servo_offsets: Tuple[float, float, float] = (0, 0, 0),
        use_plate_angles=False,
    ):
        self.servo_offsets: Tuple[float, float, float] = servo_offsets
        self.use_plate_angles = use_plate_angles

        self.menu_btn: bool = False
        self.joy_btn: bool = False
        self.joy_x: float = 0
        self.joy_y: float = 0

        # Attempt to open the spidev bus
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(spi_bus, spi_device)
            self.spi.max_speed_hz = spi_max_speed_hz
        except:
            raise IOError(f"Could not open `/dev/spidev{spi_bus}.{spi_device}`.")

        # Attempt to setup the GPIO pins and initialize the runtime
        try:
            setupGPIO()
        except:
            raise IOError(f"Could not setup GPIO pins")

        runtime()

    def close(self):
        self.spi.close()
        gpio.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def transceive(self, packet: Union[List, np.ndarray]):
        """
        Send and receive 9 bytes from hat.
        """
        # packet = right_pad_array(packet, length=9, dtype=np.int8)
        time.sleep(0.001)
        hat_to_pi = self.spi.xfer(packet.tolist())
        self._save_buttons(hat_to_pi)

    def _save_buttons(self, hat_to_pi):
        # Check if buttons are pressed
        self.menu_btn = hat_to_pi[0] == Button.MENU
        self.joy_btn = hat_to_pi[0] == Button.JOYSTICK
        # Get x & y coordinates of joystick normalized to [-1, +1]
        self.joy_x = _uint8_to_int8(hat_to_pi[JoystickByteIndex.X]) / 100
        self.joy_y = _uint8_to_int8(hat_to_pi[JoystickByteIndex.Y]) / 100

    def poll_buttons(self):
        """
        Check whether buttons are pressed and the joystick x & y values in the
        response.

        Return:
            - menu_btn: Bool
            - joy_btn : Bool
            - joy_x   : Float normalized from -1 to +1
            - joy_y   : Float normalized from -1 to +1
        """
        return self.menu_btn, self.joy_btn, self.joy_x, self.joy_y

    def enable_servos(self):
        """ Set the plate to track plate angles. """
        self.transceive(
            np.array(
                [SendCommand.SERVO_ENABLE, 0, 0, 0, 0, 0, 0, 0, 0],
                dtype=np.int8,
            )
        )

    def disable_servos(self):
        """ Disables the power to the servos. """
        self.transceive(
            np.array(
                [SendCommand.SERVO_DISABLE, 0, 0, 0, 0, 0, 0, 0, 0],
                dtype=np.int8,
            )
        )

    def set_angles(self, plate_x: float, plate_y: float):
        # If set_plate_angles flag is set, use the plate to servo conversion on
        # the hat, otherwise use the one in Python

        if self.use_plate_angles:
            # Take into account offsets when converting from degrees to values sent to hat
            plate_x, plate_y = _xy_offsets(plate_x, plate_y, self.servo_offsets)
            plate_x, plate_y = -plate_x, -plate_y
            self.transceive(
                np.array(
                    [SendCommand.SET_PLATE_ANGLES, plate_x, plate_y, 0, 0, 0, 0, 0, 0],
                    dtype=np.uint8,
                )
            )

        else:
            s1, s2, s3 = plate_angles_to_servo_positions(plate_x, plate_y)
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
            np.array(
                [
                    SendCommand.SET_SERVOS,
                    servo3_centi_degrees_high_byte,
                    servo3_centi_degrees_low_byte,
                    servo1_centi_degrees_high_byte,
                    servo1_centi_degrees_low_byte,
                    servo2_centi_degrees_high_byte,
                    servo2_centi_degrees_low_byte,
                    0,
                    0,
                ],
                dtype=np.uint8,
            )
        )

    def set_servo_offsets(self, servo1: int, servo2: int, servo3: int):
        """
        Set post-factory calibration offsets for each servo.
        Normally this call should not be needed.
        """
        self.servo_offsets = (servo1, servo2, servo3)

    def set_icon_text(self, icon_idx: Icon, text_idx: Text):
        self.transceive(
            np.array(
                [SendCommand.TEXT_ICON_SELECT, icon_idx, text_idx, 0, 0, 0, 0, 0, 0],
                dtype=np.int8,
            )
        )

    def hover(self):
        """
        Set the plate to its hover position.
        This was experimentally found to be 150 (down but still leaving some
        space at the bottom).
        """
        self.set_servos(150, 150, 150)
        # Give enough time for the action to be taken
        time.sleep(0.200)  # Experimentally found

    def lower(self):
        """
        Set the plate to its lower position (usually powered-off state).
        This was experimentally found to be 155 (lowest possible position).
        """
        self.set_servos(155, 155, 155)
        # Give enough time for the action to be taken
        time.sleep(0.200)  # Experimentally found

    def print_arbitrary_string(self, s: str):
        s = s.upper()  # The firware currently only has uppercase fonts
        s = bytes(s, "utf-8")
        s += b"\0"  # Ensure a trailing termination character
        assert len(s) <= 256

        # Calculate the number of messages required to send the text
        num_msgs = int(np.ceil(len(s) / 8))

        # Pad the message with trailing termination chars to so we always
        # send in 9 bytes increments (1 byte control, 8 bytes data)
        s += (num_msgs * 8 - len(s)) * b"\0"

        for msg_idx in range(num_msgs):
            # Combine into one list to send
            msg = [SendCommand.ARBITRARY_MESSAGE] + s[8 * msg_idx : 8 * msg_idx + 8]
            self.transceive(msg)

        # After sending all buffer info, send the command to display the buffer
        self.transceive(
            np.array(
                [SendCommand.DISPLAY_BUFFER],
                dtype=np.int8,
            )
        )

    def print_info_screen(self):
        sw_major, sw_minor, sw_bug = _get_sw_version()
        ip1, ip2, ip3, ip4 = _get_host_ip()
        self.print_arbitrary_string(
            f"PROJECT MOAB\n"
            f"SW VERSION\n{sw_major}.{sw_minor}.{sw_bug}\n"
            f"IP ADDRESS:\n{ip1}.{ip2}.{ip3}.{ip4}\n"
        )
