#ifndef PI_MSGR_H_
#define PI_MSGR_H_

#include <zephyr.h>
#include <stdbool.h>


// Messaging from the Pi to the hat --------------------------------------------
#define NOOP					0x00
#define SERVO_ENABLE			0x01	// The servos should be turned off
#define SERVO_DISABLE			0x02	// The servos should be turned on
#define CONTROL_INFO			0x03	// This packet contains control info
#define SET_PLATE_ANGLES		0x04	// Set the plate angles (x and y angles)
#define SET_SERVOS				0x05	// Set the servo positions manually

#define COPY_STRING				0x80	// There is a arbitrary length string being transmitted (max len 240 bytes) and copy into the text buffer
#define DISPLAY_BIG_TEXT_ICON	0x81    // Display what is currently in the buffer (large font) along with an icon sent in this message. Does not scroll.
#define DISPLAY_BIG_TEXT		0x82    // Display only what is currently in the buffer (large font). Does not scroll.
#define DISPLAY_SMALL_TEXT      0x83    // Display only what is currently in the buffer (small font). Scroll if required.
#define DISPLAY_POWER_SYMBOL    0x84    // Display text (and icon) using one of the five IEC Power Symbols now in Unicode 9.0, as "0"..."5"


typedef union
{
	struct
	{
		u8_t icon; // Selects 1 icon out of (currently) 8 options
	};
	struct
	{
		// Both are in hundredths of a degree 
		int8_t plate_angle1; // Plate X (pitch) angle
		int8_t plate_angle2; // Plate Y (roll) angle
	};
	struct
	{
		// All are in hundredths of a degree 
		u8_t servo1_pos_centi_deg_high_byte; // Servo 1 angle (for direct servo control)
		u8_t servo1_pos_centi_deg_low_byte;
		u8_t servo2_pos_centi_deg_high_byte; // Servo 2 angle
		u8_t servo2_pos_centi_deg_low_byte;
		u8_t servo3_pos_centi_deg_high_byte; // Servo 3 angle
		u8_t servo3_pos_centi_deg_low_byte;
	};
	struct
	{
		char characters[7];
	};
	u8_t raw[7];
} pi_to_hat_data_t;

// All CONTROL packets are 8 bytes long
typedef struct
{
	u8_t control;			// 1 byte: Control byte (always the same)
	pi_to_hat_data_t data;	// 7 bytes: Data (dependent on control byte)
} pi_to_hat_t;

typedef struct
{
    u8_t menu_button;       // byte 0: 0 or 1
    u8_t joystick_button;   // byte 1: 0 or 1
    int8_t joystick_x;		// byte 2: Joystick X (-100 to +100)
    int8_t joystick_y;		// byte 3: Joystick Y (-100 to +100)
    u8_t padding[4];        // byte 4-7: always 0
} hat_to_pi_t;

int wait_for_pi_message(pi_to_hat_t* msg, int32_t timeout);

#endif
