// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <drivers/clock_control/stm32_clock_control.h>

#include "pwm/pwm_stm32.h"
#include "stm32f4xx_hal_tim.h"


/* ---- */
#include <zephyr.h>
#include <drivers/pwm.h>
#include <drivers/gpio.h>
#include <math.h>

#include <logging/log.h>
LOG_MODULE_REGISTER(plate);


#include "joystick.h"
#include "plate.h"

#define SERVO_EN_PORT	DT_ALIAS_SERVO_ENABLE_GPIOS_CONTROLLER
#define SERVO_EN_PIN	DT_ALIAS_SERVO_ENABLE_GPIOS_PIN

/* size of stack area used by this thread */
#define STACKSIZE 1024

/* scheduling priority used by this thread */
#define PRIORITY 8

/* Microsecond timing for the PWM module */
#define PERIOD 3300
#define MINPULSEWIDTH 375
#define MAXPULSEWIDTH 2400
#define SERVO_DEGREES 180
#define SERVO_DEAD_WIDTH 4
#define TYPICAL_MAX		2250
#define TYPICAL_MID		1950
#define TYPICAL_MIN		1450

#define PW_PER_DEGREE (MAXPULSEWIDTH - MINPULSEWIDTH) / SERVO_DEGREES

#define DT_ALIAS_PWM_3_LABEL DT_INST_0_ST_STM32_PWM_LABEL

#define ARM_LENGTH		55.0
#define PLATE_DIAMETER 	197.3
#define SIDE_LENGTH		170.87
#define PIVOT_HEIGHT 	80.0
#define SQRT3			1.732050808
#define ANGLE_MAX		160
#define ANGLE_MIN		90
#define ARM_TRAVEL		70.0

#define PI 3.14159265358979323846

#define OTP_BASE_ADDR	0x1FFF7800
#define OTP_BANK_SIZE	0x20
#define OTP_LOCK_ADDR	0x1FFF7A00

#define DEV_DATA(dev) ((struct pwm_stm32_data * const)(dev)->driver_data)

static struct device *plate_servo_en_dev;

typedef struct
{
	struct device *dev;
	u32_t pwm_channel;
} servo_t;

static servo_t plate_servos[3];
static float servo_usec_degree[3];

servo_cal_t servocal;

static int plate_update_pw_stm32(struct device* dev, int channel, u32_t pulse_width)
{
	struct pwm_stm32_data *data = DEV_DATA(dev);
	TIM_HandleTypeDef *TimerHandle = &data->hpwm;
	static u64_t pulse_cycles = 0;
	static u64_t cycles_per_sec = 0;
	int err = 0;
	uint32_t tim_chan = TIM_CHANNEL_1;

	if (channel == 1)
		tim_chan = TIM_CHANNEL_2;
	else if (channel == 2)
		tim_chan = TIM_CHANNEL_3;
	else if (channel == 3)
		tim_chan = TIM_CHANNEL_4;

	if (pwm_get_cycles_per_sec(dev, channel, &cycles_per_sec) != 0)
	{
		return -EIO;
	}

	pulse_cycles = (pulse_width * cycles_per_sec) / USEC_PER_SEC;
	if (pulse_cycles >= ((u64_t)1 << 32)) {
		return -ENOTSUP;
	}

	__HAL_TIM_SET_COMPARE(TimerHandle, tim_chan, (u32_t)pulse_cycles);

	return err;
}

static inline float plate_to_degrees(float radians)
{
    return radians * (180.0 / PI);
}

static inline float plate_to_radians(float degrees)
{
	return degrees * PI / 180.0;
}

static void plate_coerce_to_range(float* value, float low, float high)
{
	if (*value < low)
		*value = low;
	else if (*value > high)
		*value = high;
}

static void plate_compute_servo_angles(float theta_x, float theta_y, float* servo_angles)
{
	static float z1, z2, z3, r;

	const float sin_theta_y = sin(plate_to_radians(-theta_y));
	const float sin_theta_x = sin(plate_to_radians(theta_x));

	z1 = PIVOT_HEIGHT + sin_theta_y * (SIDE_LENGTH / SQRT3);
	r = PIVOT_HEIGHT - sin_theta_y * (SIDE_LENGTH / ( 2 * SQRT3));
	z2 = r + sin_theta_x * (SIDE_LENGTH / 2);
	z3 = r - sin_theta_x * (SIDE_LENGTH / 2);

	if (z1 > (2 * ARM_LENGTH)) z1 = (2 * ARM_LENGTH);
	if (z2 > (2 * ARM_LENGTH)) z2 = (2 * ARM_LENGTH);
	if (z3 > (2 * ARM_LENGTH)) z3 = (2 * ARM_LENGTH);

	servo_angles[0] = 180 - plate_to_degrees(asin(z1 / (2 * ARM_LENGTH)));
	servo_angles[1] = 180 - plate_to_degrees(asin(z2 / (2 * ARM_LENGTH)));
	servo_angles[2] = 180 - plate_to_degrees(asin(z3 / (2 * ARM_LENGTH)));
}

static int plate_servo_set_position(u8_t id, float angle)
{
	int err = 0;
	u32_t pulse_width;
	servo_t servo;

	plate_coerce_to_range(&angle, ANGLE_MIN, ANGLE_MAX);
	//LOG_INF("channel %d @ %d degrees", id, (int)angle);

	//pulse_width = (angle * servo_usec_degree[id]) + MINPULSEWIDTH;
	pulse_width = ((angle - ANGLE_MIN) * servo_usec_degree[id]) + servocal.servo_min[id];
	servo = plate_servos[id];

	if ((err = pwm_pin_set_usec(servo.dev, servo.pwm_channel, PERIOD, pulse_width/*, PWM_POLARITY_NORMAL*/)) != 0)
	{
			LOG_ERR("pwm pin set fails");
	}

	return err;
}

int plate_servo_update_position(u8_t id, float angle)
{
	int err = 0;
	u32_t pulse_width;
	servo_t servo;

	// Comment out this line, to remove servo limitations
	plate_coerce_to_range(&angle, ANGLE_MIN, ANGLE_MAX);
	//LOG_INF("channel %d @ %d degrees", id, (int)angle);

	pulse_width = ((angle - ANGLE_MIN) * servo_usec_degree[id]) + servocal.servo_min[id];

	servo = plate_servos[id];

	if ((err = plate_update_pw_stm32(servo.dev, id, pulse_width)) != 0)
	{
			LOG_ERR("pwm update fails");
	}

	return err;
}

int plate_set_angle(float theta_x, float theta_y)
{
	int err = 0;
	float servo_angles[3] = { 0, 0, 0 };

	//LOG_INF("setting plate angle to %d, %d", (int)theta_x, (int)theta_y);

	plate_compute_servo_angles(theta_x, theta_y, &servo_angles[0]);

	/* This was changed to update the "wrong" servos in order to rotate
	everything 120 degrees */
	if ((err = plate_servo_update_position(0, /*servo_angles[0]*/servo_angles[2])) != 0)
	{
		return err;
	}

	if ((err = plate_servo_update_position(1, /*servo_angles[1]*/servo_angles[0])) != 0)
	{
		return err;
	}

	if ((err = plate_servo_update_position(2, /*servo_angles[2]*/servo_angles[1])) != 0)
	{
		return err;
	}

	return err;
}

int plate_servo_enable(u8_t enable)
{
	return gpio_pin_write(plate_servo_en_dev, SERVO_EN_PIN, (u32_t)enable);
}

int plate_init(void)
{
	struct device *pwm_dev;
	u32_t i;
	char cal[sizeof(servo_cal_t)];
	int bank = 1;
	uint32_t address = (OTP_LOCK_ADDR + bank);
	unsigned char c;
	int cal_invalid = 0;

	plate_servo_en_dev = device_get_binding(SERVO_EN_PORT);

	if (!plate_servo_en_dev) {
		LOG_ERR("Cannot find servo enable device!");
		return -1;
	}

	gpio_pin_configure(plate_servo_en_dev, SERVO_EN_PIN, GPIO_DIR_OUT);

	pwm_dev = device_get_binding(DT_ALIAS_PWM_3_LABEL);
	if (!pwm_dev) {
		LOG_ERR("Cannot find PWM device!");
		return -1;
	}
	
	/* If there's no calibration data, we will leave these "default" values
	as the calibration */
	for (i=0; i<3; i++)
	{
		servocal.servo_max[i] = TYPICAL_MAX;
		servocal.servo_133[i] = TYPICAL_MID;
		servocal.servo_min[i] = TYPICAL_MIN;
	}
	
	bank = 15;
	address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	for (i=0; i<8; i++)
	{
		c = *(unsigned char *)address;
		//LOG_INF ("0x%08X = %02X", address, c);
		if (c == 0xFF) bank-=2;
		else break;
		address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	}
	/* Actual servo calibration values are in increments of 5 so we will never
	   see a value of 0xFF if the calibration data is present in OTP */
	if (*(unsigned char *)address != 0xFF)
	{
		for (i=0; i<sizeof(servo_cal_t); i++) {
			cal[i] = *(unsigned char *)address++;
		}
		memcpy(&servocal, &cal, sizeof(servo_cal_t));
		for (i=0; i<3; i++) 
		{
			if ((servocal.servo_max[i] > MAXPULSEWIDTH) || (servocal.servo_max[i] < MINPULSEWIDTH)) cal_invalid = 1;
			if ((servocal.servo_min[i] > MAXPULSEWIDTH) || (servocal.servo_min[i] < MINPULSEWIDTH)) cal_invalid = 1;
			if ((servocal.servo_133[i] > MAXPULSEWIDTH) || (servocal.servo_133[i] < MINPULSEWIDTH)) cal_invalid = 1;
		}
	}
	
	if (cal_invalid) 
	{
		LOG_ERR("Servo calibration data is corrupt! Using defaults.");
		for (i=0; i<3; i++)
		{
			servocal.servo_max[i] = TYPICAL_MAX;
			servocal.servo_133[i] = TYPICAL_MID;
			servocal.servo_min[i] = TYPICAL_MIN;
		}
	}

	for (i=0; i<3; i++)	
        LOG_INF ("Bank: %i Servo %i: Max %i Mid %i Min %i", bank, i, servocal.servo_max[i], servocal.servo_133[i], servocal.servo_min[i]);

	servo_usec_degree[0] = (servocal.servo_max[0] - servocal.servo_min[0])/ARM_TRAVEL;
	servo_usec_degree[1] = (servocal.servo_max[1] - servocal.servo_min[1])/ARM_TRAVEL;
	servo_usec_degree[2] = (servocal.servo_max[2] - servocal.servo_min[2])/ARM_TRAVEL;

	plate_servos[0].dev = pwm_dev;
	plate_servos[0].pwm_channel = 1;

	plate_servos[1].dev = pwm_dev;
	plate_servos[1].pwm_channel = 2;

	plate_servos[2].dev = pwm_dev;
	plate_servos[2].pwm_channel = 3;

	plate_servo_set_position(0, 150);
	plate_servo_set_position(1, 150);
	plate_servo_set_position(2, 150);

	return 0;
}
