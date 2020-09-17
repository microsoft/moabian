# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import math
import cython
from enum import IntEnum
from typing import Tuple

ctypedef char bool
ctypedef signed char int8_t
ctypedef unsigned char uint8_t

cdef extern from "moab.h":
    int moab_init();

    void moab_setIcon(int icon);
    void moab_setText(int text);
    void moab_activatePlate();
    void moab_disableServoPower();
    void moab_setPlateAngles(int8_t plate_x_deg, int8_t plate_y_deg);
    void moab_setServoPositions(uint8_t servo1_pos, uint8_t servo2_pos, uint8_t servo3_pos);
    void moab_setServoOffsets(int8_t servo1_offset, int8_t servo2_offset, int8_t servo3_offset);

    int moab_sync();

    int moab_getMenuBtn();
    int moab_getJoystickBtn();
    int moab_getJoystickX();
    int moab_getJoystickY();

    int moab_pollPowerBtn();
    void moab_enableFan(bool enabled);
    void moab_enableHat(bool enabled);
    float moab_pollTemp();

class Result(IntEnum):
    OK = 0
    UNKNOWN_ERROR = 1
    INVALID_ARG = 2

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

def init() -> Result:
    """
    Initializes the library.
    Call once at startup.

    return OK on success.
    """
    return Result(moab_init())

def activatePlate():
    """ Set the plate to track plate angles. """
    moab_activatePlate()

def hoverPlate():
    """
    Set the plate to its hover position. 
    This was experimentally found to be 150 (down but still leaving some 
    space at the bottom).
    """
    moab_setServoPositions(150, 150, 150)

def lowerPlate():
    """
    Set the plate to its lower position (usually powered-off state). 
    This was experimentally found to be 155 (lowest possible position).
    """
    moab_setServoPositions(155, 155, 155)

def disableServoPower():
    """ Disables the power to the servos. """
    moab_disableServoPower()

def setPlateAngles(plate_x_deg: int, plate_y_deg: int):
    moab_setPlateAngles(plate_x_deg, plate_y_deg)

def setServoPositions(servo1_pos: int, servo2_pos: int, servo3_pos: int):
    moab_setServoPositions(servo1_pos, servo2_pos, servo3_pos)

def setServoOffsets(servo1_offset: int, servo2_offset: int, servo3_offset: int):
    """
    Set post-factory calibration offsets for each servo.
    Can be called before init().

    Normally this call should not be needed.
    """
    moab_setServoOffsets(servo1_offset, servo2_offset, servo3_offset)

def setIcon(icon_idx: Icon):
    moab_setIcon(icon_idx)

def setText(text_idx: Text):
    moab_setText(text_idx)

def sync() -> Result:
    """
    Sets the current state on the hardware and polls
    the current control states.

    return OK on success.
    """
    return Result(moab_sync())

def getMenuBtn() -> bool:
    return True if moab_getMenuBtn() else False

def getJoystickBtn() -> bool:
    return True if moab_getJoystickBtn() else False

def getJoystickX() -> float:
    return moab_getJoystickX() / 100.0

def getJoystickY() -> float:
    return moab_getJoystickY() / 100.0

def enableFan(enabled: bool):
    moab_enableFan(enabled)

def enableHat(enabled: bool):
    moab_enableHat(enabled)

def pollTemp() -> float:
    return moab_pollTemp()

def pollPowerBtn() -> bool:
    return True if moab_pollPowerBtn() else False


cdef float _bandpass_lookup[256]
cdef float _last_sigma = 0.0
cdef float _last_gain = 0.0
cdef unsigned char _last_center = 0

@cython.boundscheck(False)
@cython.wraparound(False)
def _update_bandpass_lookup(unsigned char center, float sigma, float gain):
    global _bandpass_lookup
    global _last_center
    global _last_gain
    global _last_sigma

    _last_center = center
    _last_sigma = sigma
    _last_gain = gain

    mu = 0.5
    for n in range(256):
        h = n / 255.0

        # rotate the hue phase so that `center` is at 0.5
        h = h + (0.5 - (center / 255.0))
        if (h > 1.0):
            h = h - 1.0
        if (h < 0.0):
            h = h + 1.0
            
        # gaussian bandpass filter
        f = math.exp(-( (h - mu)**2 / ( 2.0 * sigma**2 ) ) )

        # pre-gain around center
        f = f * gain
        if f > 1.0:
            f = 1.0

        _bandpass_lookup[n] = f


@cython.boundscheck(False)
@cython.wraparound(False)
def hue_mask(unsigned char [:, :, :] image, unsigned char center, float sigma, float gain, float mask_gain):
    global _bandpass_lookup

    # set the variable extension types
    cdef int x, y, n, width, height
    cdef float h, s, v, mu, f
    cdef unsigned char mask, ih

    # grab the image dimensions
    height = image.shape[0]
    width = image.shape[1]
    
    # generate a lookup table for center, sigma & gain
    if (center != _last_center or sigma != _last_sigma or gain != _last_gain):
        _update_bandpass_lookup(center, sigma, gain)

    for y in range(0, height):
        for x in range(0, width):
            # pull each component out as a float [0..1]
            ih = image[y, x, 0]
            s = image[y, x, 1] / 255.0
            v = image[y, x, 2] / 255.0

            # map from [0..255] -> [0..1] through lookup table
            # this applies the bandpass filter on hue
            h = _bandpass_lookup[ih]

            # mask the hue with sat, val and apply another gain filter
            f = (h * s * v) * mask_gain
            if f > 1.0:
                f = 1.0

            # covert back to char space
            mask = <unsigned char>(f * 255)
            image[y, x, 0] = mask
            image[y, x, 1] = mask
            image[y, x, 2] = mask

    # return the thresholded image
    return image
