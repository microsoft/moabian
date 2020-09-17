// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <math.h>
#include <string.h>
#include "startup.h"
#include "moab.h"
#include "spi.h"


#ifdef __cplusplus
extern "C" {
#endif

static int8_t _servo1_offset = 0;
static int8_t _servo2_offset = 0;
static int8_t _servo3_offset = 0;

static int8_t _plate_x_deg = 0;
static int8_t _plate_y_deg = 0;

static send_packet_standard _spi_out = {0};
static receive_packet_type _spi_in = {0};

#define X_TILT_SERVO1 -0.5
#define Y_TILT_SERVO2 0.866 
#define Y_TILT_SERVO3 -0.866 

#define PLATE_X_OFFSET(x) (x + (_servo1_offset + (int8_t)(X_TILT_SERVO1 * _servo2_offset) + (int8_t)(X_TILT_SERVO1 * _servo3_offset)))
#define PLATE_Y_OFFSET(y) (y + ((int)(Y_TILT_SERVO2 * _servo2_offset) + (int)(Y_TILT_SERVO3 * _servo3_offset)))

int moab_init()
{
    // Initialize GPIO
    gpio_init();

    // Set mode to runtime, not bootloader
    runtime();

    // clear IO structures
    memset(&_spi_out, 0, sizeof(_spi_out));
    memset(&_spi_in, 0, sizeof(_spi_in));
    
    // init state: servos disabled
    _spi_out.display.icon = MOAB_ICON_BLANK;
    _spi_out.display.text = MOAB_TXT_INIT;

    // set plate angles based on current offsets
    _plate_x_deg = 0;
    _plate_y_deg = 0;
    _spi_out.plate_angle_x = PLATE_X_OFFSET(_plate_x_deg);
    _spi_out.plate_angle_y = PLATE_Y_OFFSET(_plate_y_deg);

    delay(250);
    return MOAB_RESULT_OK;
}

// call to set current state and get current input
int moab_sync()
{
    transceive_packet(_spi_out.combined_packet, _spi_in.combined_packet, SEND_PACKET_BYTES);
    return MOAB_RESULT_OK;
}

void moab_setIcon(int icon)
{
    _spi_out.display.icon = icon;
}

void moab_setText(int text)
{
    _spi_out.display.text = text;
}

void moab_activatePlate()
{
    _spi_out.control.servo_en = 1;
    _spi_out.control.servo_control = 0;
    // _spi_out.plate_angle_x and
    // _spi_out.plate_angle_y will be restored
}

void moab_setPlateAngles(int8_t plate_x_deg, int8_t plate_y_deg)
{
    _spi_out.control.servo_en = 1;
    _spi_out.control.servo_control = 0;

    _plate_x_deg = plate_x_deg;
    _plate_y_deg = plate_y_deg;
    _spi_out.plate_angle_x = PLATE_X_OFFSET(_plate_x_deg);
    _spi_out.plate_angle_y = PLATE_Y_OFFSET(_plate_y_deg);

    // _spi_out.servoX_pos will now be ignored.
}

void moab_setServoPositions(uint8_t servo1_pos, uint8_t servo2_pos, uint8_t servo3_pos)
{
    // instead of using plate_angle_x,y set raw servo positions
    _spi_out.control.servo_en = 1;
    _spi_out.control.servo_control = 1;

    _spi_out.servo1_pos = servo1_pos;
    _spi_out.servo2_pos = servo2_pos;
    _spi_out.servo3_pos = servo3_pos;
}

void moab_setServoOffsets(int8_t servo1_offset, int8_t servo2_offset, int8_t servo3_offset)
{
    _servo1_offset = servo1_offset;
    _servo2_offset = servo2_offset;
    _servo3_offset = servo3_offset;
}

int moab_getMenuBtn() { return _spi_in.buttons.menu; }
int moab_getJoystickBtn() { return _spi_in.buttons.joystick; }
int moab_getJoystickX() { return _spi_in.joystick_x; }
int moab_getJoystickY() { return _spi_in.joystick_y; }

int moab_pollPowerBtn() {
    int power = PIN_READ(HAT_PWR_N);
    return power != 1;
}

void moab_disableServoPower()
{
    _spi_out.control.servo_en = 0;
}

void moab_enableFan(bool enabled)
{
    if (enabled)
        SET_HIGH(FAN_EN);
    else
        SET_LOW(FAN_EN);
}

void moab_enableHat(bool enabled)
{
    if (enabled)
        SET_HIGH(HAT_EN);
    else
        SET_LOW(HAT_EN);
}

float moab_pollTemp()
{
    float millideg;
	FILE *thermal;

    thermal = fopen("/sys/class/thermal/thermal_zone0/temp","r");
    if( thermal > 0)
    {
        fscanf(thermal,"%f",&millideg);
        fclose(thermal);

        return millideg / 1000.0;
    }

    return NAN;
}

#ifdef __cplusplus
}
#endif
