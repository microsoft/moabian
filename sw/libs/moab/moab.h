// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include "stdbool.h"
#include "stdint.h"

#define EXPORT __attribute__((visibility("default")))

// Result values
#define MOAB_RESULT_OK 0
#define MOAB_RESULT_UNKNOWN_ERROR 1
#define MOAB_RESULT_INVALID_ARG 2

// Icons available to display
#define MOAB_ICON_BLANK 0
#define MOAB_ICON_UP_DOWN 1
#define MOAB_ICON_DOWN 2
#define MOAB_ICON_UP 3
#define MOAB_ICON_DOT 4
#define MOAB_ICON_PAUSE 5
#define MOAB_ICON_CHECK 6
#define MOAB_ICON_X 7

// Predefined text strings available to display
#define MOAB_TXT_BLANK 0
#define MOAB_TXT_INIT 1
#define MOAB_TXT_POWER_OFF 2
#define MOAB_TXT_ERROR 3
#define MOAB_TXT_CAL 4
#define MOAB_TXT_MANUAL 5
#define MOAB_TXT_CLASSIC 6
#define MOAB_TXT_BRAIN 7
#define MOAB_TXT_CUSTOM1 8
#define MOAB_TXT_CUSTOM2 9
#define MOAB_TXT_INFO 10
#define MOAB_TXT_CAL_INSTR 11
#define MOAB_TXT_CAL_COMPLETE 12
#define MOAB_TXT_CAL_CANCELED 13
#define MOAB_TXT_CAL_FAILED 14
#define MOAB_TXT_VERS_IP_SN 15
#define MOAB_TXT_UPDATE_BRAIN 16
#define MOAB_TXT_UPDATE_SYSTEM 17

EXPORT int moab_init();

EXPORT void moab_setIcon(int icon);
EXPORT void moab_setText(int text);
EXPORT void moab_activatePlate();
EXPORT void moab_disableServoPower();
EXPORT void moab_setPlateAngles(int8_t plate_x_deg, int8_t plate_y_deg);
EXPORT void moab_setServoPositions(uint8_t servo1_pos, uint8_t servo2_pos, uint8_t servo3_pos);
EXPORT void moab_setServoOffsets(int8_t servo1_offset, int8_t servo2_offset, int8_t servo3_offset);

EXPORT int moab_sync();

EXPORT int moab_getMenuBtn();
EXPORT int moab_getJoystickBtn();
EXPORT int moab_getJoystickX();
EXPORT int moab_getJoystickY();

EXPORT void moab_enableFan(bool enabled);
EXPORT void moab_enableHat(bool enabled);
EXPORT float moab_pollTemp();
EXPORT int moab_pollPowerBtn();

EXPORT void send_ip_address(uint8_t ip1, uint8_t ip2, uint8_t ip3, uint8_t ip4);
EXPORT void send_sw_version(uint8_t sw_major, uint8_t sw_minor, uint8_t sw_bug);

