#ifndef DISP_H_
#define DISP_H_

#include <zephyr.h>

typedef enum
{
    MOABSYMBOL = 0,
    IECSYMBOL,
    DIN_18,
    DIN_12,
} our_fonts_t;

// Glyphs for Moab Symbols
typedef enum
{
	DISP_ICON_BLANK = 0,
	DISP_ICON_UP_DOWN,
	DISP_ICON_DOWN,
	DISP_ICON_UP,
	DISP_ICON_DOT,
	DISP_ICON_PAUSE,
	DISP_ICON_CHECK,
	DISP_ICON_X,
	DISP_ICON_EOL           // TODO: I don't think we need sentinel with enum in C
} disp_icon_t;

// Glyphs for IEC Power Symbols
// https://unicodepowersymbol.com/
typedef enum
{
	IEC_ICON_POWER  = 0,   // ⏻
	IEC_ICON_TOGGLE_POWER, // ⏼
	IEC_ICON_POWER_ON,     // ⏽
	IEC_ICON_SLEEP_MODE,   // ⏾
	IEC_ICON_POWER_OFF,    // ⭘
	IEC_ICON_EOL           // (sentinel)
} disp_power_icon_t;

typedef enum
{
	DISP_TXT_BLANK = 0,
	DISP_TXT_INIT,
	DISP_TXT_POWER_OFF,
	DISP_TXT_ERROR,
	DISP_TXT_CAL,
	DISP_TXT_MANUAL,
	DISP_TXT_CLASSIC,
	DISP_TXT_BRAIN,
	DISP_TXT_CUSTOM1,
	DISP_TXT_CUSTOM2,
	DISP_TXT_BOT_INFO,
	DISP_TXT_CAL_INSTR,
	DISP_TXT_CAL_COMPLETE,
	DISP_TXT_CAL_CANCLED,
	DISP_TXT_CAL_FAILED,
	DISP_TXT_INFO_SCREEN,
	DISP_TXT_BRAIN_UPDATED,
	DISP_TXT_SYSTEM_UPDATED,
	DISP_TXT_MOABV2,
	DISP_TXT_EOL, // end of list
	DISP_TXT_ARBITRARY // hack to support arbitrary strings
} disp_text_t;

// void disp_set_icon(disp_icon_t icon);
// void disp_set_text(disp_text_t text);
// void display_buffer(const char *str);
void display_big_text_icon(const char *str, disp_icon_t i);
void display_big_text(const char *str);
void display_small_text(const char *str);
void display_power_symbol(const char *str, disp_power_icon_t i);


#endif
