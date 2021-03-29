#ifndef __SH1106_REGS_H__
#define __SH1106_REGS_H__

#define SH1106_CONTROL_LAST_BYTE_CMD		0x00
#define SH1106_CONTROL_LAST_BYTE_DATA		0x40
#define SH1106_CONTROL_BYTE_CMD				0x80
#define SH1106_CONTROL_BYTE_DATA			0xc0
#define SH1106_READ_STATUS_MASK				0xc0
#define SH1106_READ_STATUS_BUSY				0x80
#define SH1106_READ_STATUS_ON				0x40

/*
 * Fundamental Command Table
 */
#define SH1106_SET_CONTRAST_CTRL			0x81 /* double byte command */

#define SH1106_SET_ENTIRE_DISPLAY_OFF		0xa4
#define SH1106_SET_ENTIRE_DISPLAY_ON		0xa5

#define SH1106_SET_NORMAL_DISPLAY			0xa6
#define SH1106_SET_REVERSE_DISPLAY			0xa7

#define SH1106_DISPLAY_OFF					0xae
#define SH1106_DISPLAY_ON					0xaf

/*
 * Addressing Setting Command Table
 */
#define SH1106_SET_LOWER_COL_ADDRESS		0x00
#define SH1106_SET_LOWER_COL_ADDRESS_MASK	0x0f

#define SH1106_SET_HIGHER_COL_ADDRESS		0x10
#define SH1106_SET_HIGHER_COL_ADDRESS_MASK	0x0f

#define SH1106_SET_MEM_ADDRESSING_MODE		0x20 /* double byte command */
#define SH1106_SET_MEM_ADDRESSING_HORIZONTAL	0x00
#define SH1106_SET_MEM_ADDRESSING_VERTICAL	0x01
#define SH1106_SET_MEM_ADDRESSING_PAGE		0x02

#define SH1106_SET_COLUMN_ADDRESS		0x21 /* triple byte command */

#define SH1106_SET_PAGE_ADDRESS		0x22 /* triple byte command */

#define SH1106_SET_PAGE_START_ADDRESS		0xb0
#define SH1106_SET_PAGE_START_ADDRESS_MASK	0x07


/*
 * Hardware Configuration Command Table
 */
#define SH1106_SET_START_LINE			0x40
#define SH1106_SET_START_LINE_MASK		0x3f

#define SH1106_SET_SEGMENT_MAP_NORMAL		0xa0
#define SH1106_SET_SEGMENT_MAP_REMAPED		0xa1

#define SH1106_SET_MULTIPLEX_RATIO		0xa8 /* double byte command */

#define SH1106_SET_COM_OUTPUT_SCAN_NORMAL	0xc0
#define SH1106_SET_COM_OUTPUT_SCAN_FLIPPED	0xc8

#define SH1106_SET_DISPLAY_OFFSET		0xd3 /* double byte command */

#define SH1106_SET_PADS_HW_CONFIG		0xda /* double byte command */
#define SH1106_SET_PADS_HW_SEQUENTIAL		0x02
#define SH1106_SET_PADS_HW_ALTERNATIVE		0x12


/*
 * Timming and Driving Scheme Setting Command Table
 */
#define SH1106_SET_CLOCK_DIV_RATIO		0xd5 /* double byte command */

#define SH1106_SET_CHARGE_PERIOD		0xd9 /* double byte command */

#define SH1106_SET_VCOM_DESELECT_LEVEL		0xdb /* double byte command */

#define SH1106_NOP				0xe3

/*
 * Charge Pump Command Table
 */
#define SH1106_SET_CHARGE_PUMP_ON		0x8d /* double byte command */
#define SH1106_SET_CHARGE_PUMP_ON_DISABLED	0x10
#define SH1106_SET_CHARGE_PUMP_ON_ENABLED	0x14

#define SH1106_SET_DCDC_MODE			0xad /* double byte command */
#define SH1106_SET_DCDC_DISABLED		0x8a
#define SH1106_SET_DCDC_ENABLED			0x8b

#define SH1106_SET_PUMP_VOLTAGE_64		0x30
#define SH1106_SET_PUMP_VOLTAGE_74		0x31
#define SH1106_SET_PUMP_VOLTAGE_80		0x32
#define SH1106_SET_PUMP_VOLTAGE_90		0x33

/*
 * Read modify write
 */
#define SH1106_READ_MODIFY_WRITE_START		0xe0
#define SH1106_READ_MODIFY_WRITE_END		0xee

/* time constants in ms */
#define SH1106_RESET_DELAY			100

#endif // __SH1106_REGS_H__
