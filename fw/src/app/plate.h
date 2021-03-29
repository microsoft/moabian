#ifndef SERVO_H_
#define SERVO_H_

#include <zephyr.h>

typedef struct servo_cal
{
	u16_t servo_min[3];
	u16_t servo_133[3];
	u16_t servo_max[3];
} servo_cal_t;

int plate_init(void);
int plate_servo_enable(u8_t enable);
int plate_servo_update_position(u8_t id, float angle);
int plate_set_angle(float theta_x, float theta_y);

//int plate_sweep_sync_servos(float* target_servo_angles);
//int plate_sync_angle(float theta_x, float theta_y);

#endif
