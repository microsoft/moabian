// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "plate.h"
#include "joystick.h"
#include "display.h"
#include "app_version.h"

LOG_MODULE_REGISTER(shell);

#define OTP_BASE_ADDR   0x1FFF7800
#define OTP_BANK_SIZE   0x20
#define OTP_LOCK_ADDR   0x1FFF7A00

#define TYPICAL_MAX		2250
#define TYPICAL_MID		1950
#define TYPICAL_MIN		1450
#define MINPULSEWIDTH   375
#define MAXPULSEWIDTH   2400

extern joystick_cal_t calibration;
joystick_cal_t otp_cal;
volatile uint32_t * flash_cr = (uint32_t *)0x40023C10;
volatile uint32_t * flash_sr = (uint32_t *)0x40023C0C;

// Plate commands

static int cmd_plate_enable(const struct shell *shell)
{
    return plate_servo_enable(1);
}

static int cmd_plate_disable(const struct shell *shell)
{
    return plate_servo_enable(0);
}

static int cmd_plate_servo_angle(const struct shell *shell, size_t argc, char **argv)
{
    int err = 0;
    u8_t id = 0;
    float angle = 0.0;

    if (argc < 3)
    {
        shell_error(shell, "Invalid number of arguments.");
        return -EINVAL;
    }

    id = atoi(argv[1]);
    angle = atoi(argv[2]);

    if ((id < 0) | (id > 2))
    {
        shell_error(shell, "Invalid servo id (0-2).");
        return -EINVAL;
    }

    if ((angle < 0) | (angle > 180))
    {
        shell_error(shell, "Invalid servo angle (0-180).");
        return -EINVAL;
    }

    if ((err = plate_servo_update_position(id, angle)) != 0)
    {
        shell_error(shell, "Failed to set servo %d.  Err = %d", id, err);
        return -EINVAL;
    }

    return err;
}

SHELL_STATIC_SUBCMD_SET_CREATE(sub_plate,
    SHELL_CMD(enable, NULL, "Enable servos.", cmd_plate_enable),
    SHELL_CMD(enable, NULL, "Disable servos.", cmd_plate_disable),
    SHELL_CMD(servo, NULL, "Set the angle of a servo. ", cmd_plate_servo_angle),
    SHELL_SUBCMD_SET_END /* Array terminated. */
);
SHELL_CMD_REGISTER(plate, &sub_plate, "Plate control commands", NULL);


// Joystick Commands

static int cmd_joystick_position(const struct shell *shell, size_t argc, char **argv)
{
    int err = 0;
    int8_t x, y;


    if ((err = joystick_position(&x, &y, &calibration)) != 0)
    {
        shell_error(shell, "Failed to read joystick.  Err = %d", err);
        return err;
    }

    shell_print(shell, "x = %d, y = %d", (int)x, (int)y);

    return err;
}

SHELL_CMD_REGISTER(joystick, NULL, "Read joystick position", cmd_joystick_position);


// Kernel Commands

static int cmd_version(const struct shell *shell, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    shell_print(shell, "Moab version %s", APP_SEMVER);

    return 0;
}

SHELL_CMD_ARG_REGISTER(version, NULL, "Show kernel version", cmd_version, 1, 0);


// Non-volatile memory banks (OTP)

void print_bank(const struct shell *sh, u8_t bank)
{
    uint32_t address = (OTP_BASE_ADDR + (bank * OTP_BANK_SIZE));
    uint8_t otp[32];
    memcpy(&otp, (const void *)address, sizeof(otp));

    shell_print(sh, "Bank %i", bank);

    shell_print(sh, "0x%08X: %02X %02X %02X %02X %02X %02X %02X %02X\r", address,
        otp[0], otp[1], otp[2], otp[3], otp[4], otp[5], otp[6], otp[7]);

    shell_print(sh, "0x%08X: %02X %02X %02X %02X %02X %02X %02X %02X\r", address+8,
        otp[8], otp[9], otp[10], otp[11], otp[12], otp[13], otp[14], otp[15]);

    shell_print(sh, "0x%08X: %02X %02X %02X %02X %02X %02X %02X %02X\r", address+16,
        otp[16], otp[17], otp[18], otp[19], otp[20], otp[21], otp[22], otp[23]);

    shell_print(sh, "0x%08X: %02X %02X %02X %02X %02X %02X %02X %02X\r\n", address+24,
        otp[24], otp[25], otp[26], otp[27], otp[28], otp[29], otp[30], otp[31]);
}

/* "banks" will print the contents of the OTP flash. Simply calling it with no
   arguments will output all 16 banks; with one argument will output one single
   bank, and with two arguments will print from bank %1 to bank %2. */

static int cmd_banks(const struct shell *sh, size_t argc, char **argv)
{
    // no arguments: show all banks
    if (argc-1 == 0)
    {
        for (u8_t i = 0; i < 16; i++)
        {
            print_bank(sh, i);
        }
    }

    // 1 arg: show one bank
    if (argc-1 == 1)
    {
        uint8_t bank = atoi(argv[1]);
        if ((bank < 0) | (bank > 15))
        {
            shell_error(sh, "Invalid bank (0-15): %d", bank);
            return -EINVAL;
        }
        print_bank(sh, bank);

    }

    // 2 args: show range of banks
    if (argc-1 == 2)
    {
        u8_t b1 = atoi(argv[1]);
        u8_t b2 = atoi(argv[2]);

        if ((b1 < 0) | (b1 > 15) | (b2 < 0) | (b2 > 15))
        {
            shell_error(sh, "Invalid bank range (0-15) (0-15): %d %d", b1, b2);
            return -EINVAL;
        }

        if (b1 > b2)
        {
            shell_error(sh, "Bank %d must be less than %d", b1, b2);
            return -EINVAL;
        }

        for (u8_t i = b1; i <= b2; i++)
        {
            print_bank(sh, i);
        }

    }

    return 0;
}

SHELL_CMD_REGISTER(banks, NULL, "Print OTP banks [0-15]", cmd_banks);

/* "calibjoy" searches OTP flash for the most recent joystick calibration and
   outputs the values it finds (if any). Mostly useful for debugging. */

static int cmd_calibjoy(const struct shell *sh, size_t argc, char **argv)
{
    joystick_cal_t pizza; // This variable name was Scott's idea, don't blame me

	int bank = 14;
	int i;
	char cal[sizeof(joystick_cal_t)];
	char c;
	uint32_t address = (OTP_BASE_ADDR + (OTP_BANK_SIZE*bank));

	shell_print(sh, "starting.");
	bank = 14;
	for (i=0; i<8; i++)
	{
		c = *(unsigned char *)address;
		if (c == 0xCB)
		{
			break;
		}
		else
		{
			bank-=2;
		}
		address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	}

	if (*(unsigned char *)address != 0xCB) {
		shell_print(sh, "Could not find calibration data");
		pizza.x_error = (0);
		pizza.y_error = (0);
		pizza.xp_scale = (0.5);
		pizza.xn_scale = (0.5);
		pizza.yp_scale = (0.5);
		pizza.yn_scale = (0.5);
	}
	else
	{
		shell_print(sh, "Found calibration data in bank %i", bank);
		address++;
		for (i=0; i<sizeof(joystick_cal_t); i++)
		{
			cal[i] = *(unsigned char *)address++;
		}
		memcpy(&pizza, &cal, sizeof(joystick_cal_t));
	}


    // Now use the print code from above
    shell_print(sh, "x_error = %i", pizza.x_error);
    shell_print(sh, "y_error = %i", pizza.y_error);

    /* We scale the float value by 10000 (so that e.g. 0.5 will print as 5000)
       because like basically every microcontroller libc implementation the
       Zephyr printf functions do not support floating point. */

    int32_t scale;
    scale = pizza.xp_scale*10000.0;
    shell_print(sh, "xp_scale = %i", scale);

    scale = pizza.xn_scale*10000.0;
    shell_print(sh, "xn_scale = %i", scale);

    scale = pizza.yp_scale*10000.0;
    shell_print(sh, "yp_scale = %i", scale);

    scale = pizza.yn_scale*10000.0;
    shell_print(sh, "yn_scale = %i", scale);

    return 0;
}

SHELL_CMD_REGISTER(calibjoy, NULL, "Parse joystick calibration bank", cmd_calibjoy);

/* "calibservo" will read out the most recently written servo calibration, to
   verify that what was written is actually being used by the system. */

static int cmd_calibservo(const struct shell *sh, size_t argc, char **argv)
{
    servo_cal_t servocal;

	int bank = 15;
	int i;
    int cal_invalid = 0;
	char cal[sizeof(servo_cal_t)];
	char c;
	uint32_t address = (OTP_BASE_ADDR + (OTP_BANK_SIZE*bank));

	shell_print(sh, "starting.");

	address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	for (i=0; i<8; i++)
	{
		c = *(unsigned char *)address;
		if (c == 0xFF) bank-=2;
		else break;
		address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	}
	/* Actual servo calibration values are in increments of 5 so we will never
	   see a value of 0xFF if the calibration data is present in OTP */
	if (*(unsigned char *)address != 0xFF)
	{
		shell_print (sh, "Found servo cal data in bank %i", bank);
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
		shell_error(sh, "Servo calibration data is corrupt! Setting to defaults");
		for (i=0; i<3; i++)
		{

			servocal.servo_max[i] = TYPICAL_MAX;
			servocal.servo_133[i] = TYPICAL_MID;
			servocal.servo_min[i] = TYPICAL_MIN;
		}
	}

	for (i=0; i<3; i++)	shell_print(sh, "Servo %i: Max %i Mid %i Min %i", i, servocal.servo_max[i], servocal.servo_133[i], servocal.servo_min[i]);
    return 0;
}

SHELL_CMD_REGISTER(calibservo, NULL, "Show servo calibration bank", cmd_calibservo);

/* "resetservo" will write a set of default servo calibration values to the next available OTP bank.
   This is useful in cases where the bot simply refuses to calibrate properly.

   Since this is potentially destructive and, at present, not recoverable ex-
   cept by performing another calibration, this command will not work unless
   you feed it the right password, which is "shazam" at Scott's suggestion. */

static int cmd_resetservo(const struct shell *sh, size_t argc, char **argv)
{
    servo_cal_t servocal;

	int i;
    char cal[sizeof(servo_cal_t)];
	char c;
	uint32_t address = (OTP_BASE_ADDR + (OTP_BANK_SIZE));

    if (argc != 2)
    {
        shell_error(sh, "Syntax: resetservo password");
        return -EINVAL;
    }

    if (strncmp(argv[1], "shazam", 6))
    {
        shell_error(sh, "Error: password incorrect");
        return -EINVAL;
    }

    shell_print(sh, "Password accepted");

    for (i=0; i<3; i++)
    {

        servocal.servo_max[i] = TYPICAL_MAX;
        servocal.servo_133[i] = TYPICAL_MID;
        servocal.servo_min[i] = TYPICAL_MIN;
    }

    // Addition: This seems to be a better default setting for S0
    servocal.servo_min[0] -= 50;
	servocal.servo_max[0] -= 50;
	servocal.servo_133[0] -= 50;

    for (i=0; i<8; i++)
    {
        c = *(unsigned char *)address;
        if (c == 0xFF) break;
        else address+=(OTP_BANK_SIZE*2);
    }
    shell_print(sh, "Writing OTP bank %i", (i*2)+1);
    *flash_cr = 0x00000001;
    memcpy(&cal, &servocal, sizeof(servo_cal_t));
    for (i=0; i<sizeof(servo_cal_t); i++)
    {
        while (*flash_sr & 0x00010000);
        *(unsigned char *)address = cal[i];
        address++;
    }
    return 0;
}
SHELL_CMD_REGISTER(resetservo, NULL, "Write defaults to servo calibration", cmd_resetservo);


// string command

static int cmd_string_big(const struct shell *sh, size_t argc, char **argv)
{
    // no arguments: show "Hello World"
    if (argc-1 == 0)
        display_big_text("Hello Big World");

    if (argc-1 == 1)
        display_big_text(argv[1]);

    return 0;
}

static int cmd_string_small(const struct shell *sh, size_t argc, char **argv)
{
    // no arguments: show "Hello World"
    if (argc-1 == 0)
        display_small_text("Hello Small World");

    if (argc-1 == 1)
        display_small_text(argv[1]);

    return 0;
}

SHELL_STATIC_SUBCMD_SET_CREATE(sub_string,
    SHELL_CMD(big, NULL, "big", cmd_string_big),
    SHELL_CMD(small, NULL, "small", cmd_string_small),
    SHELL_SUBCMD_SET_END
);
SHELL_CMD_REGISTER(string, &sub_string, "Display string", NULL);

