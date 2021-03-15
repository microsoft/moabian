// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "state.h"
#include "joystick.h"
#include "spi.h"

LOG_MODULE_REGISTER(joystick);

#define ADC_RESOLUTION 12
#define ADC_MAX 4095
#define ADC_MAX_VOLT 3.3
#define ADC_VOLT_BIT (ADC_MAX_VOLT / ADC_MAX)
#define JOY_CENTER_VOLTS (ADC_MAX_VOLT / 2.0)
#define JOY_X_CHANNEL 0
#define JOY_Y_CHANNEL 1
#define OTP_BASE_ADDR	0x1FFF7800
#define OTP_BANK_SIZE	0x20
#define OTP_LOCK_ADDR	0x1FFF7A00

#define TYPICAL_90		1500
#define TYPICAL_160		2250

/* size of stack area used by the thread */
#define STACKSIZE 1024

/* scheduling priority used by the thread */
#define PRIORITY 9


static struct device *adc;
static struct adc_channel_cfg ch_x_cfg;
static struct adc_channel_cfg ch_y_cfg;
static u16_t adc_buffer;
joystick_cal_t calibration;

static struct adc_sequence adc_table;

static struct gpio_callback gpio_cb_joystick;
static struct gpio_callback gpio_cb_menu;

// TODO: good comment here
// https://devzone.nordicsemi.com/f/nordic-q-a/54146/blink-led-on-button-press-on-nrf9160dk
// helped me on button up and down
// trigger callback on pin rising *and* falling: GPIO_INT_DOUBLE_EDGE

// 4 buttons, 4 leds
// https://github.com/leonyoliveir/Embebbed-Systems/blob/fb797537b7818d7a6f15c9978d2152b2c3dafcc7/io_exercise/src/main.c

#define EDGE    (GPIO_INT | GPIO_INT_EDGE | GPIO_INT_DEBOUNCE)
#define JOY_BTN_PORT DT_ALIAS_BUTTON_JOYSTICK_GPIOS_CONTROLLER
#define JOY_BTN_PIN DT_ALIAS_BUTTON_JOYSTICK_GPIOS_PIN
#define JOY_BTN_FLAGS (DT_ALIAS_BUTTON_JOYSTICK_GPIOS_FLAGS | EDGE | GPIO_PUD_PULL_UP)
#define MENU_BTN_PORT DT_ALIAS_BUTTON_MENU_GPIOS_CONTROLLER
#define MENU_BTN_PIN DT_ALIAS_BUTTON_MENU_GPIOS_PIN
#define MENU_BTN_FLAGS (DT_ALIAS_BUTTON_MENU_GPIOS_FLAGS | EDGE | GPIO_PUD_PULL_UP)


static void menu_button_pressed(struct device *gpio, struct gpio_callback *cb, u32_t pins)
{
    int state = 0;
    gpio_pin_read(gpio, MENU_BTN_PIN, &state);
    atomic_set(&g_btn_menu, state);
}

static void joy_button_pressed(struct device *gpio, struct gpio_callback *cb, u32_t pins)
{
    int state = 0;
    gpio_pin_read(gpio, JOY_BTN_PIN, &state);
    atomic_set(&g_btn_joy, state);
}

static int joy_button_init(struct device *gpio_dev)
{
    // Likely need gpio_int_double_edge 
	gpio_pin_configure(gpio_dev, JOY_BTN_PIN, 
            (GPIO_DIR_IN | 
             GPIO_INT_ACTIVE_HIGH |                                 // from moab_hat.dts
             GPIO_INT | GPIO_INT_EDGE | GPIO_INT_DEBOUNCE |         // from EDGE
             GPIO_INT_DOUBLE_EDGE |
             GPIO_PUD_PULL_UP));

    // gpio_pin_interrupt_configure is called here in the sample code
    // https://github.com/zephyrproject-rtos/zephyr/blob/master/samples/basic/button/src/main.c
    // why is it missing here?

	gpio_init_callback(&gpio_cb_joystick, joy_button_pressed, BIT(JOY_BTN_PIN));
	gpio_add_callback(gpio_dev, &gpio_cb_joystick);
	gpio_pin_enable_callback(gpio_dev, JOY_BTN_PIN);

	return 0;
}

static int menu_button_init(struct device *gpio_dev)
{
	gpio_pin_configure(gpio_dev, MENU_BTN_PIN, 
            (GPIO_DIR_IN | 
            GPIO_INT_ACTIVE_HIGH |                                 // from moab_hat.dts
            GPIO_INT | GPIO_INT_EDGE | GPIO_INT_DEBOUNCE |         // from EDGE
            GPIO_INT_DOUBLE_EDGE |
            GPIO_PUD_PULL_UP));

	gpio_init_callback(&gpio_cb_menu, menu_button_pressed, BIT(MENU_BTN_PIN));
	gpio_add_callback(gpio_dev, &gpio_cb_menu);
	gpio_pin_enable_callback(gpio_dev, MENU_BTN_PIN);

	return 0;
}


int joystick_position(int8_t* x_percent, int8_t* y_percent, joystick_cal_t *cal)
{
	int err = 0;
	u16_t analog_val_x, analog_val_y;
	float xscale, yscale;

	/* Configure ADC table structure */
	adc_table.channels = BIT(JOY_X_CHANNEL);
	adc_table.resolution = ADC_RESOLUTION;
	adc_table.buffer = &adc_buffer;
	adc_table.buffer_size = sizeof(adc_buffer);

	if ((err = adc_read(adc, &adc_table)) != 0)
		return err;

	analog_val_x = adc_buffer;

	/* Configure ADC table structure */
	adc_table.channels = BIT(JOY_Y_CHANNEL);

	if ((err = adc_read(adc, &adc_table)) != 0)
		return err;

	analog_val_y = adc_buffer;

	if (cal)
	{
		analog_val_x -= (cal->x_error);
		analog_val_y -= (cal->y_error);

	}

	float vx = analog_val_x * ADC_VOLT_BIT;
	float vy = analog_val_y * ADC_VOLT_BIT;

	xscale = 1.0;
	yscale = 1.0;

	if (cal)
	{
		if ((vx - JOY_CENTER_VOLTS) > 0) xscale = cal->xn_scale;
		else xscale = cal->xp_scale;
		if ((vy - JOY_CENTER_VOLTS) > 0) yscale = cal->yn_scale;
		else yscale = cal->yp_scale;
	}

	// Remove the joystick's calibrated offset error
	*x_percent = -(int8_t)(((vx - JOY_CENTER_VOLTS) * (100 / JOY_CENTER_VOLTS))/xscale);
	*y_percent = -(int8_t)(((vy - JOY_CENTER_VOLTS) * (100 / JOY_CENTER_VOLTS))/yscale);

	/* This operation removing the joystick's offset error can (and in the past
	   has) caused rollover errors by over- or underflowing. The next bit will
	   check for that and clamp the value to +100% or -100% as needed. */

	// Check for int underflow (+offset)
	if (analog_val_x > 10000) {
		*x_percent = 100;
	} else if (analog_val_x > ADC_MAX) { // also for overflow of the ADC's max value (-offset)
		*x_percent = -100;
	}

	if (analog_val_y > 10000) {
		*y_percent = 100;
	} else if (analog_val_y > ADC_MAX) {
		*y_percent = -100;
	}

	// Sanity check to clamp percent values to max. 100% in either direction
	if (*x_percent > 100) {
		*x_percent = 100;
	}

	if (*x_percent < -100) {
		*x_percent = -100;
	}

	if (*y_percent > 100) {
		*y_percent = 100;
	}

	if (*y_percent < -100) {
		*y_percent = -100;
	}

	return err;
}

static int adc_init(void)
{
	int err = 0;

	adc = device_get_binding(DT_ADC_1_NAME);

	if (adc == NULL)
	{
		LOG_ERR("Failed to get ADC device.");
		return -EINVAL;
	}

	/* Configure ADC channels */
	ch_x_cfg.channel_id =	JOY_X_CHANNEL;
	ch_x_cfg.differential = false;
	ch_x_cfg.gain = ADC_GAIN_1,
	ch_x_cfg.reference = ADC_REF_INTERNAL;
	ch_x_cfg.acquisition_time = ADC_ACQ_TIME_DEFAULT;

	ch_y_cfg.channel_id =	JOY_Y_CHANNEL;
	ch_y_cfg.differential = false;
	ch_y_cfg.gain = ADC_GAIN_1,
	ch_y_cfg.reference = ADC_REF_INTERNAL;
	ch_y_cfg.acquisition_time = ADC_ACQ_TIME_DEFAULT;

	if ((err = adc_channel_setup(adc, &ch_x_cfg)) != 0)
		return err;

	err = adc_channel_setup(adc, &ch_y_cfg);

	return err;
}

static void joy_task(void)
{
	struct device *joy_gpio_dev;
	struct device *menu_gpio_dev;
	int8_t joyx, joyy;
	int err;
	int bank = 14;
	int i;
	char cal[sizeof(joystick_cal_t)];
	char c;
	uint32_t address = (OTP_BASE_ADDR + (OTP_BANK_SIZE*bank));

	/* Start searching for calibration data at bank 14 and work downwards. This
       makes sure we're always looking at the most recent valid calibration. */
	bank = 14;
	for (bank = 14; bank >=0; bank -= 2)
	{
		c = *(unsigned char *)address;

		// 0xCB is a magic value that indicates the beginning of calibration data
		if (c == 0xCB)
		{
			break;
		}

		address = (OTP_BASE_ADDR + (OTP_BANK_SIZE * bank));
	}

	if (*(unsigned char *)address != 0xCB) {
		LOG_ERR ("Joystick calibration not found");
		/* These are default pre-calibration values for the joystick */
		calibration.x_error = (0);
		calibration.y_error = (0);
		calibration.xp_scale = (0.5);
		calibration.xn_scale = (0.5);
		calibration.yp_scale = (0.5);
		calibration.yn_scale = (0.5);
	}
	else
	{
		LOG_INF ("Found calibration data in bank: %i", bank);
		address++; // skip over magic byte
		for (i=0; i<sizeof(joystick_cal_t); i++)
		{
			cal[i] = *(unsigned char *)address++;
		}
		memcpy(&calibration, &cal, sizeof(joystick_cal_t));
	}
	joy_gpio_dev = device_get_binding(JOY_BTN_PORT);
	if (!joy_gpio_dev)
	{
		LOG_ERR("Error getting joystick button port.");
		return;
	}

	joy_button_init(joy_gpio_dev);

	menu_gpio_dev = device_get_binding(MENU_BTN_PORT);
	if (!menu_gpio_dev)
	{
		LOG_ERR("Error getting menu button port.");
		return;
	}

	menu_button_init(menu_gpio_dev);

	if (adc_init() != 0)
		LOG_ERR("ADC failed Init.");

	// Read joystick at 60 Hz
	while(true)
	{
		if ((err = joystick_position(&joyx, &joyy, &calibration)) == 0)
		{
            // def'n of these two functions need mutexes to protect them
            // TODO: test this new version
            atomic_set(&g_joy_x, joyx);
            atomic_set(&g_joy_y, joyy);


            // not thread safe. menu/joy buttons are set in callbacks
			// pi_msgr_set_joystick(joyx, joyy);      // main.c
			// pi_msgr_set_buttons(button_data);      // pi_msgr.c
			// button_data.raw = 0;
		}
		else
		{
			LOG_WRN("Failed to read joystick.  code = %d", err);
		}

        k_sleep(16);        // 60 Hz
        //k_sleep(33);        // 30 Hz
	}
}

K_THREAD_DEFINE(joy_task_id, STACKSIZE, joy_task, NULL, NULL, NULL, PRIORITY, 0, K_NO_WAIT);
