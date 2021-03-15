// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <logging/log.h>
LOG_MODULE_REGISTER(sh1106, CONFIG_DISPLAY_LOG_LEVEL);

#include <string.h>
#include <device.h>
#include <init.h>
#include <drivers/gpio.h>
#include <drivers/spi.h>
#include <display/cfb.h>

#include "sh1106_regs.h"

#define SH1106_SPI_FREQ DT_INST_0_SINO_SH1106_SPI_MAX_FREQUENCY

/* -- CS Pin -- */
//#ifdef DT_INST_0_SINO_SH1106_CS_GPIOS_CONTROLLER
#define SH1106_CS_CONTROLLER DT_INST_0_SINO_SH1106_CS_GPIOS_CONTROLLER
#define SH1106_CS_PIN DT_INST_0_SINO_SH1106_CS_GPIOS_PIN
#define SH1106_CS_FLAGS DT_INST_0_SINO_SH1106_CS_GPIOS_FLAGS
//#endif

/* -- Reset Pin -- */
#define SH1106_RESET_CONTROLLER DT_INST_0_SINO_SH1106_RESET_GPIOS_CONTROLLER
#define SH1106_RESET_PIN DT_INST_0_SINO_SH1106_RESET_GPIOS_PIN
#define SH1106_RESET_FLAGS DT_INST_0_SINO_SH1106_RESET_GPIOS_FLAGS

/* -- A0 Pin (4-wire mode) -- */
//#ifdef DT_INST_0_SINO_SH1106_A0_GPIOS
#define SH1106_4WIRE
#define SH1106_A0_CONTROLLER DT_INST_0_SINO_SH1106_A0_GPIOS_CONTROLLER
#define SH1106_A0_PIN DT_INST_0_SINO_SH1106_A0_GPIOS_PIN
#define SH1106_A0_FLAGS DT_INST_0_SINO_SH1106_A0_GPIOS_FLAGS
//#endif

//#define CONFIG_SH1106_REVERSE_MODE

#ifndef CONFIG_SH1106_DEFAULT_CONTRAST
#define CONFIG_SH1106_DEFAULT_CONTRAST 0xAF
#endif

#if DT_INST_0_SINO_SH1106_SEGMENT_REMAP == 1
#define SH1106_PANEL_SEGMENT_REMAP	true
#else
#define SH1106_PANEL_SEGMENT_REMAP	false
#endif

#if DT_INST_0_SINO_SH1106_COM_INVDIR == 1
#define SH1106_PANEL_COM_INVDIR	true
#else
#define SH1106_PANEL_COM_INVDIR	false
#endif

#if DT_INST_0_SINO_SH1106_COM_SEQUENTIAL == 1
#define SH1106_COM_PINS_HW_CONFIG	SH1106_SET_PADS_HW_SEQUENTIAL
#else
#define SH1106_COM_PINS_HW_CONFIG	SH1106_SET_PADS_HW_ALTERNATIVE
#endif

#define SH1106_PANEL_NUMOF_PAGES	(DT_INST_0_SINO_SH1106_HEIGHT / 8)
#define SH1106_CLOCK_DIV_RATIO		0x1
#define SH1106_CLOCK_FREQUENCY		0x9
#define SH1106_PANEL_VCOM_DESEL_LEVEL	0x25
#define SH1106_PANEL_PUMP_VOLTAGE	SH1106_SET_PUMP_VOLTAGE_90

#define SH1106_BUF_SIZE	(SH1106_PANEL_NUMOF_PAGES * )


#define SH1106_PANEL_NUMOF_COLUMS	132


#ifndef SH1106_ADDRESSING_MODE
#define SH1106_ADDRESSING_MODE		(SH1106_SET_MEM_ADDRESSING_HORIZONTAL)
#endif

struct sh1106_data {
//#ifdef SH1106_4WIRE
	struct device *a0;
//#endif
	struct device *cs;
	struct spi_cs_control cs_ctrl;
	struct device *reset;
	struct device *spi;
	struct spi_config spi_cfg;
	u8_t contrast;
	u8_t scan_mode;
};

static int sh1106_spi_write(const struct device *dev, const u8_t *data, size_t length)
{
	struct sh1106_data *driver = dev->driver_data;
	
	const struct spi_buf buf[1] = 
	{
		{
			.buf = data,
			.len = length
		}
	};

	struct spi_buf_set tx = 
	{
		.buffers = buf,
	};

	tx.count = 1;

	return spi_write(driver->spi, &driver->spi_cfg, &tx);
}

static int sh1106_cmd_write(const struct device *dev, const u8_t *data, size_t length)
{
	struct sh1106_data *driver = dev->driver_data;

	gpio_pin_write(driver->a0, SH1106_A0_PIN, 0);
	return sh1106_spi_write(dev, data, length);
}

static int sh1106_data_write(const struct device *dev, const u8_t *data, size_t length)
{
	struct sh1106_data *driver = dev->driver_data;

	gpio_pin_write(driver->a0, SH1106_A0_PIN, 1);
	return sh1106_spi_write(dev, data, length);
}

static inline int sh1106_set_panel_orientation(const struct device *dev)
{
	u8_t cmd_buf[] = {
		(SH1106_PANEL_SEGMENT_REMAP ?
		 SH1106_SET_SEGMENT_MAP_REMAPED :
		 SH1106_SET_SEGMENT_MAP_NORMAL),
		(SH1106_PANEL_COM_INVDIR ?
		 SH1106_SET_COM_OUTPUT_SCAN_FLIPPED :
		 SH1106_SET_COM_OUTPUT_SCAN_NORMAL)
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

static inline int sh1106_set_timing_setting(const struct device *dev)
{
	u8_t cmd_buf[] = {
		SH1106_SET_CLOCK_DIV_RATIO,
		(SH1106_CLOCK_FREQUENCY << 4) | SH1106_CLOCK_DIV_RATIO,
		SH1106_SET_CHARGE_PERIOD,
		DT_INST_0_SINO_SH1106_PRECHARGEP,
		SH1106_SET_VCOM_DESELECT_LEVEL,
		SH1106_PANEL_VCOM_DESEL_LEVEL
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

static inline int sh1106_set_hardware_config(const struct device *dev)
{
	u8_t cmd_buf[] = {
		SH1106_SET_START_LINE,
		SH1106_SET_DISPLAY_OFFSET,
		DT_INST_0_SINO_SH1106_DISPLAY_OFFSET,
		SH1106_SET_PADS_HW_CONFIG,
		SH1106_COM_PINS_HW_CONFIG,
		SH1106_SET_MULTIPLEX_RATIO,
		DT_INST_0_SINO_SH1106_MULTIPLEX_RATIO
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

static inline int sh1106_set_charge_pump(const struct device *dev)
{
	u8_t cmd_buf[] = {
		SH1106_SET_CHARGE_PUMP_ON,
		SH1106_SET_CHARGE_PUMP_ON_ENABLED,
		SH1106_SET_DCDC_MODE,
		SH1106_SET_DCDC_ENABLED,
		SH1106_PANEL_PUMP_VOLTAGE,
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

int sh1106_resume(const struct device *dev)
{
	/* set display on */
	u8_t cmd_buf[] = { SH1106_DISPLAY_ON };
	
	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

int sh1106_suspend(const struct device *dev)
{
	/* set display off */
	u8_t cmd_buf[] = { SH1106_DISPLAY_OFF };

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

int sh1106_set_pos(const struct device *dev, const u16_t x, const u16_t y)
{
	//struct sh1106_data *driver = dev->driver_data;

	u16_t column = x;
	u8_t page = y;

	/* set posistion command */
	u8_t cmd_buf[] = 
	{ 
		SH1106_SET_PAGE_START_ADDRESS + page,
		SH1106_SET_HIGHER_COL_ADDRESS_MASK & column,
		SH1106_SET_HIGHER_COL_ADDRESS | (column >> 4)
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

int sh1106_write_page(const struct device *dev, u8_t page, void const *data, size_t length)
{
	u8_t cmd_buf[] =
	{
		SH1106_SET_LOWER_COL_ADDRESS | (DT_INST_0_SINO_SH1106_SEGMENT_OFFSET & SH1106_SET_LOWER_COL_ADDRESS_MASK),
		SH1106_SET_HIGHER_COL_ADDRESS | ((DT_INST_0_SINO_SH1106_SEGMENT_OFFSET  >> 4) & SH1106_SET_LOWER_COL_ADDRESS_MASK),
		SH1106_SET_PAGE_START_ADDRESS | page
	};

	if (page >= SH1106_PANEL_NUMOF_PAGES) {
		return -1;
	}

	if (length > SH1106_PANEL_NUMOF_COLUMS) {
		return -1;
	}

	if (sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf)))
	{
		return -1;
	}

	return sh1106_data_write(dev, data, length);
}

static u8_t sh1106_reverseBits(u8_t num) 
{ 
	unsigned int count = sizeof(num) * 8 - 1; 
	unsigned int reverse_num = num; 
      
	num >>= 1;  
	while(num) 
	{ 
		reverse_num <<= 1;        
		reverse_num |= num & 1; 
		num >>= 1; 
		count--; 
	} 
	reverse_num <<= count; 
	return reverse_num; 
} 


static int sh1106_write(const struct device *dev, const u16_t x, const u16_t y, const struct display_buffer_descriptor *desc, const void *buf)
{
	if (desc->pitch < desc->width)
	{
		LOG_ERR("Pitch is smaller then width");
		return -1;
	}

	if (buf == NULL || desc->buf_size == 0U)
	{
		LOG_ERR("Display buffer is not available");
		return -1;
	}

	if (desc->pitch > desc->width)
	{
		LOG_ERR("Unsupported mode");
		return -1;
	}

	u8_t row1 = y >> 3;
	u8_t row2 = (y + desc->height) >> 3;
	u16_t column1 = x;
	u16_t column2 = x + desc->width - 1;
	//const uint8_t *seg = (uint8_t*)buf;
	
	// reverse display addresses
	const u8_t* seg_end = &((uint8_t*)buf)[desc->buf_size - 1];

	for (u8_t row = row1; row < row2; row ++)
	{
		if (sh1106_set_pos(dev, column1, row))
		{
			LOG_ERR("Unable to set pos: %d, %d", x, y);
			return -1;
		}

		for (u16_t column = column1; column <= column2; column++)
		{
			// reverse data
			u8_t reversed_bits = sh1106_reverseBits(*seg_end);
			sh1106_data_write(dev, &reversed_bits, 1);
			seg_end--;
		}
	}

	return 0;
}

static int sh1106_read(const struct device *dev, const u16_t x, const u16_t y,
			const struct display_buffer_descriptor *desc, void *buf)
{
	LOG_ERR("Unsupported");
	return -ENOTSUP;
}

static void *sh1106_get_framebuffer(const struct device *dev)
{
	LOG_ERR("Unsupported");
	return NULL;
}

static int sh1106_set_brightness(const struct device *dev, const u8_t brightness)
{
	LOG_WRN("Unsupported");
	return -ENOTSUP;
}

int sh1106_set_contrast(const struct device *dev, const u8_t contrast)
{
	u8_t cmd_buf[] = {
		SH1106_SET_CONTRAST_CTRL,
		contrast,
	};

	return sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf));
}

static void sh1106_get_capabilities(const struct device *dev, struct display_capabilities *caps)
{
	memset(caps, 0, sizeof(struct display_capabilities));
	caps->x_resolution = DT_INST_0_SINO_SH1106_WIDTH;
	caps->y_resolution = DT_INST_0_SINO_SH1106_HEIGHT;
	caps->supported_pixel_formats = PIXEL_FORMAT_MONO01;
	caps->current_pixel_format = PIXEL_FORMAT_MONO01;
	caps->screen_info = SCREEN_INFO_MONO_VTILED;
}

static int sh1106_set_orientation(const struct device *dev, const enum display_orientation orientation)
{
	LOG_ERR("Unsupported");
	return -ENOTSUP;
}

static int sh1106_set_pixel_format(const struct device *dev, const enum display_pixel_format pf)
{
	if (pf == PIXEL_FORMAT_MONO01) {
		return 0;
	}
	LOG_ERR("Unsupported");
	return -ENOTSUP;
}

static int sh1106_clear(struct device *dev)
{
	u8_t page_data[DT_INST_0_SINO_SH1106_WIDTH];
	memset(page_data, 0, sizeof(page_data));

	for (size_t pidx = 0; pidx < SH1106_PANEL_NUMOF_PAGES; pidx++)
	{
		if (sh1106_write_page(dev, pidx, page_data, DT_INST_0_SINO_SH1106_WIDTH))
		{
			return -1;
		}
	}

	return 0;
}

static int sh1106_init_device(struct device *dev)
{
	struct sh1106_data *driver = dev->driver_data;

	u8_t cmd_buf[] = {
		SH1106_SET_ENTIRE_DISPLAY_OFF,
#ifdef CONFIG_SH1106_REVERSE_MODE
		SH1106_SET_REVERSE_DISPLAY,
#else
		SH1106_SET_NORMAL_DISPLAY,
#endif
	};


	/* -- Toggle Reset -- */
	gpio_pin_write(driver->reset, SH1106_RESET_PIN, 1);
	k_sleep(SH1106_RESET_DELAY);
	gpio_pin_write(driver->reset, SH1106_RESET_PIN, 0);
	k_sleep(SH1106_RESET_DELAY);
	gpio_pin_write(driver->reset, SH1106_RESET_PIN, 1);


	/* Turn display off */
	if (sh1106_suspend(dev)) {
		return -EIO;
	}

	if (sh1106_set_timing_setting(dev)) {
		return -EIO;
	}

	if (sh1106_set_hardware_config(dev)) {
		return -EIO;
	}

	if (sh1106_set_panel_orientation(dev)) {
		return -EIO;
	}

	if (sh1106_set_charge_pump(dev)) {
		return -EIO;
	}

	if (sh1106_cmd_write(dev, cmd_buf, sizeof(cmd_buf))) {
		return -EIO;
	}

	if (sh1106_set_contrast(dev, CONFIG_SH1106_DEFAULT_CONTRAST)) {
		return -EIO;
	}

	sh1106_resume(dev);

	sh1106_clear(dev);

	return 0;
}

static int sh1106_init(struct device *dev)
{
	struct sh1106_data *driver = dev->driver_data;

	LOG_DBG("");

	/* -- SPI Setup -- */
	driver->spi = device_get_binding(DT_INST_0_SINO_SH1106_BUS_NAME);
	if (!driver->spi) {
		LOG_ERR("spi device not found: %s", DT_INST_0_SINO_SH1106_BUS_NAME);
		return -EINVAL;
	}
	/* CPOL=0, CPHA=0 */
	driver->spi_cfg.operation = SPI_WORD_SET(8) | SPI_TRANSFER_MSB;
	driver->spi_cfg.frequency = SH1106_SPI_FREQ;


	/* -- SPI CS thru GPIO -- */
	driver->cs = device_get_binding(SH1106_CS_CONTROLLER);
	if (!driver->cs) {
		LOG_ERR("Unable to get GPIO SPI CS device");
		return -ENODEV;
	}

	driver->cs_ctrl.gpio_dev = driver->cs;
	driver->cs_ctrl.gpio_pin = SH1106_CS_PIN;
	driver->cs_ctrl.delay = 0U;

	driver->spi_cfg.cs = &driver->cs_ctrl;

	/* -- Reset Setup -- */
	driver->reset = device_get_binding(SH1106_RESET_CONTROLLER);
	if (!driver->reset) {
		LOG_ERR("Unable to get GPIO Reset device");
		return -ENODEV;
	}

	gpio_pin_configure(driver->reset, SH1106_RESET_PIN, GPIO_DIR_OUT);


	/* -- A0 Setup -- */
	driver->a0 = device_get_binding(SH1106_A0_CONTROLLER);
	if (!driver->a0) {
		LOG_ERR("Unable to get GPIO A0 device");
		return -ENODEV;
	}

	if (gpio_pin_configure(driver->a0, SH1106_A0_PIN, GPIO_DIR_OUT))
	{
		LOG_ERR("Unable to get configure A0 device");
		return -ENODEV;
	}

	gpio_pin_write(driver->a0, SH1106_A0_PIN, 0);

	return sh1106_init_device(dev);
}

static struct sh1106_data sh1106_driver;

static struct display_driver_api sh1106_driver_api = {
	.blanking_on = sh1106_suspend,
	.blanking_off = sh1106_resume,
	.write = sh1106_write,
	.read = sh1106_read,
	.get_framebuffer = sh1106_get_framebuffer,
	.set_brightness = sh1106_set_brightness,
	.set_contrast = sh1106_set_contrast,
	.get_capabilities = sh1106_get_capabilities,
	.set_pixel_format = sh1106_set_pixel_format,
	.set_orientation = sh1106_set_orientation,
};

DEVICE_AND_API_INIT(sh1106, DT_INST_0_SINO_SH1106_LABEL, sh1106_init,
		    &sh1106_driver, NULL,
		    POST_KERNEL, CONFIG_APPLICATION_INIT_PRIORITY,
		    &sh1106_driver_api);
