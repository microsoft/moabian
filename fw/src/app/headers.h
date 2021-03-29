#include <zephyr.h>

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <device.h>
#include <drivers/adc.h>
#include <drivers/clock_control/stm32_clock_control.h>
#include <drivers/display.h>
#include <drivers/gpio.h>
#include <drivers/pwm.h>
#include <drivers/spi.h>
#include <errno.h>
#include <inttypes.h>
#include <logging/log.h>
#include <lvgl.h>
#include <math.h>
#include <misc/printk.h>
#include <shell/shell.h>
#include <shell/shell_uart.h>
#include <sys/__assert.h>
#include <sys/printk.h>
#include <sys/util.h>
#include <version.h>
