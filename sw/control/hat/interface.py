# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import time
import socket
import spidev
import numpy as np
import RPi.GPIO as gpio

from enum import IntEnum

"""
# Messaging from the Pi to the hat ---------------------------------------------
# Data bytes (currently always 8 bytes)
union pi_msg_to_hat_data_t:
    struct:
        uint8_t icon              # Selects 1 icon out of (currently) 8 options
        uint8_t text              # Selects 1 string out of (currently) 32 options
    struct:
        int8_t plate_angle_x      # Plate X (pitch) angle
        int8_t plate_angle_y      # Plate Y (roll) angle
    struct:
        uint8_t servo1_pos        # Servo 1 angle (for direct servo control)
        uint8_t servo2_pos        # Servo 2 angle
        uint8_t servo3_pos        # Servo 3 angle
    struct:
        char characters[8]
    uint8_t raw[SEND_PACKET_BYTES - 1] # Enforce 8 byte message data

# All packets are 9 bytes long
union send_packet_standard:
    struct:
        uint8_t control           # Control byte (always the same)
        pi_msg_to_hat_data_t data # Data (dependent on control byte)
    char combined_packet[SEND_PACKET_BYTES]


# Messaging from the hat to the Pi ---------------------------------------------
#  Defining receive SPI packet
union hat_buttons:
    struct:
        uint8_t menu: 1
        uint8_t joystick: 1
        uint8_t res: 6
    char raw

union receive_packet_type:
    struct:
        hat_buttons buttons
        int8_t joystick_x
        int8_t joystick_y
    char combined_packet[RECEIVE_PACKET_BYTES]
"""


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
    FAN_EN    = 26  # Bcm 26 - RPi pin 37 - RPI_BPLUS_GPIO_J8_37
    HAT_EN    = 20  # Bcm 20 - RPi pin 38 - RPI_BPLUS_GPIO_J8_38
    HAT_RESET = 6   # Bcm 6  - RPi pin 31 - RPI_BPLUS_GPIO_J8_31
    HAT_PWR_N = 3   # Bcm 3  - RPi pin 5  - RPI_BPLUS_GPIO_J8_05


X_TILT_SERVO1 = -0.5
Y_TILT_SERVO2 = 0.866
Y_TILT_SERVO3 = -0.866
# fmt: on


# Global variables for things that are constantly polled -----------------------
_servo1_offset = 0
_servo2_offset = 0
_servo3_offset = 0
_icon_idx = 0
_text_idx = 0
spi = spidev.SpiDev()


# Helper functions -------------------------------------------------------------
def _byte_to_bits(byte):
    return bin(byte)[2:].rjust(8, "0")


def _uint8_to_int8(b):
    """
    Converts a byte to a signed int (int8) instead of unsigned int (uint8).
    """
    return b if b < 128 else (-256 + b)


def _xy_offsets(x, y):  # x & y were int8
    # fmt: off
    # for x brackets were cast to int8
    x_offset = x + _servo1_offset + (X_TILT_SERVO1 * _servo2_offset) + (X_TILT_SERVO1 * _servo3_offset)
    # for y brackets were cast to int
    y_offset = y + (Y_TILT_SERVO2 * _servo2_offset) + (Y_TILT_SERVO3 * _servo3_offset)
    # fmt: on
    return x_offset, y_offset


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


def runtime():
    """ Set mode to runtime mode (not bootloader mode). """
    gpio.output(GpioPin.HAT_EN, gpio.LOW)
    time.sleep(0.02)  # 20ms
    gpio.output(GpioPin.HAT_EN, gpio.HIGH)
    gpio.output(GpioPin.HAT_RESET, gpio.LOW)
    gpio.output(GpioPin.BOOT_EN, gpio.LOW)
    time.sleep(0.25)  # 250ms


def setupGPIO():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(
        [GpioPin.BOOT_EN, GpioPin.FAN_EN, GpioPin.HAT_EN, GpioPin.HAT_RESET], gpio.OUT
    )
    gpio.setup(GpioPin.HAT_PWR_N, gpio.IN)


def send(packet):
    """
    Send 9 bytes to hat.
    Use `writebytes2` instead of `writebytes` since it works with numpy array.
    Python immediately converts hex  to python )
    """
    assert len(packet) == 9
    return spi.writebytes2(packet)


def receive():
    """Receive 9 bytes from hat."""
    return spi.readbytes(9)


# Library functions ------------------------------------------------------------
def init(bus=0, device=0):
    """
    Initializes the library.
    Call once at startup.
    """
    setupGPIO()
    runtime()
    spi.open(bus, device)
    spi.max_speed_hz = 10000


def close():
    spi.close()
    gpio.cleanup()


def activate_plate():
    """ Set the plate to track plate angles. """
    send([SendCommand.SERVO_ENABLE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


def hover_plate():
    """
    Set the plate to its hover position.
    This was experimentally found to be 150 (down but still leaving some
    space at the bottom).
    """
    set_servo_positions(150, 150, 150)


def lower_plate():
    """
    Set the plate to its lower position (usually powered-off state).
    This was experimentally found to be 155 (lowest possible position).
    """
    set_servo_positions(155, 155, 155)


def disable_servo_power():
    """ Disables the power to the servos. """
    send([SendCommand.SERVO_DISABLE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


def set_plate_angles(plate_x_deg: int, plate_y_deg: int):
    # Take into account offsets when converting from degrees to values sent to hat
    plate_x, plate_y = _xy_offsets(plate_x_deg, plate_y_deg)
    send(
        np.array(
            [
                SendCommand.SET_PLATE_ANGLES,
                plate_x,
                plate_y,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ],
            dtype=np.int8,
        )
    )


def set_servo_positions(servo1_pos: int, servo2_pos: int, servo3_pos: int):
    send(
        np.array(
            [
                SendCommand.SET_SERVOS,
                servo1_pos,
                servo2_pos,
                servo3_pos,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ],
            dtype=np.int8,
        )
    )


def set_servo_offsets(servo1_offset: int, servo2_offset: int, servo3_offset: int):
    """
    Set post-factory calibration offsets for each servo.
    Normally this call should not be needed.
    """
    global _servo1_offset
    global _servo2_offset
    global _servo3_offset
    _servo1_offset = servo1_offset
    _servo2_offset = servo2_offset
    _servo3_offset = servo3_offset


def set_icon_text(icon_idx: Icon, text_idx: Text):
    send(
        [
            SendCommand.TEXT_ICON_SELECT,
            icon_idx,
            text_idx,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ],
    )


def sync():
    """
    Empty function that was previously needed due to the way the communications
    layer worked.
    """
    pass


# TODO: For all the buttons and joystick values, this really should be in a
#       single function that polls for everything (after all we send everything
#       all at once...)
#
# Under control/controllers/common.event.py:
# The EventDispatcher class function _raw_event calls all of these.
#     def _raw_event(self) -> Event:
#         return Event(get_menu_btn(), get_joystick_btn(), get_joystick_x(), get_joystick_y())
def get_menu_btn():
    """ Check menu button bit in the response. """
    # Send noop to ensure "fresh" values
    send([SendCommand.NOOP, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hat_to_pi = receive()
    return hat_to_pi[0] == Button.MENU


def get_joystick_btn():
    """ Check joystick button bit in the response. """
    # Send noop to ensure "fresh" values
    send([SendCommand.NOOP, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hat_to_pi = receive()
    return hat_to_pi[0] == Button.JOYSTICK


def get_joystick_x():
    """ Check joystick x value byte in the response. """
    # Send noop to ensure "fresh" values
    send([SendCommand.NOOP, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hat_to_pi = receive()
    joystick_x = _uint8_to_int8(hat_to_pi[JoystickByteIndex.X])
    return joystick_x / 100.0


def get_joystick_y():
    """ Check joystick y value byte in the response. """
    # Send noop to ensure "fresh" values
    send([SendCommand.NOOP, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hat_to_pi = receive()
    joystick_y = _uint8_to_int8(hat_to_pi[JoystickByteIndex.Y])
    return joystick_y / 100.0


def get_joystick():
    """ Check joystick x and y value bytes in the response. """
    # Send noop to ensure "fresh" values
    send([SendCommand.NOOP, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hat_to_pi = receive()
    joystick_x = _uint8_to_int8(hat_to_pi[JoystickByteIndex.X])
    joystick_y = _uint8_to_int8(hat_to_pi[JoystickByteIndex.Y])
    return joystick_x / 100.0, joystick_y / 100.0


def enable_fan(enabled: bool):
    gpio.output(GpioPin.FAN_EN, gpio.HIGH if enabled else gpio.LOW)


def enable_hat(enabled: bool):
    gpio.output(GpioPin.HAT_EN, gpio.HIGH if enabled else gpio.LOW)


def poll_temp():
    temp = 0
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
        temp = int(file.read()) / 1000.0
    return temp


def poll_power_btn():
    return gpio.input(GpioPin.HAT_PWR_N) != gpio.HIGH


def print_arbitrary_message(s):
    s = bytes(s, "utf-8")
    s += b"\0"
    assert len(s) < 256

    # Calculate the number of messages required to send the message
    num_msgs = int(np.ceil(len(s) / 8))

    # Fill the message with trailing termination chars to so we always
    # send 9 bytes
    s += (num_msgs * 8 - len(s)) * b"\0"

    for msg_idx in range(num_msgs):
        send([SendCommand.ARBITRARY_MESSAGE, *s[8 * msg_idx : 8 * msg_idx + 8]])


def print_ip():
    ip1, ip2, ip3, ip4 = _get_host_ip()
    send_ip_address(ip1, ip2, ip3, ip4)
    print_arbitrary_message(f"PROJECT MOAB\n\nIP ADDRESS:\n{ip1}.{ip2}.{ip3}.{ip4}")


def print_sw_version():
    sw_major, sw_minor, sw_bug = _get_sw_version()
    print_arbitrary_message(f"PROJECT MOAB\n\nSW VERSION\n{sw_major}{sw_minor}{sw_bug}")


def print_info_screen():
    sw_major, sw_minor, sw_bug = _get_sw_version()
    ip1, ip2, ip3, ip4 = _get_host_ip()
    print_arbitrary_message(
        f"PROJECT MOAB\n\nSW VERSION\n{sw_major}{sw_minor}{sw_bug}\n\nIP ADDRESS:\n{ip1}.{ip2}.{ip3}.{ip4}"
    )