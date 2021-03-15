#ifndef JOY_IO_H_
#define JOY_IO_H_

#include <zephyr.h>

typedef struct joystick_cal
{
	int16_t x_error;
	int16_t y_error;
	float xp_scale;
	float xn_scale;
	float yp_scale;
	float yn_scale;
 } joystick_cal_t;


int joystick_position(int8_t* x_percent, int8_t* y_percent, joystick_cal_t *cal);

#endif
