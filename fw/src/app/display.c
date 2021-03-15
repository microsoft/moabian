// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "display.h"

LOG_MODULE_REGISTER(display);

// Mutex to protect access from other threads
struct k_mutex mutex1;

// The SH1106 device handle
static struct device *display_dev;

// Three fonts used on the display
LV_FONT_DECLARE(din2014_18)
LV_FONT_DECLARE(din2014light_12)
LV_FONT_DECLARE(moabsym_30)
LV_FONT_DECLARE(iecsymbol_30)

// The icon and text label GUI handles
static lv_obj_t* icon_label;
static lv_obj_t* text_label;
static lv_style_t icon_style;
static lv_style_t text_style;

// For the display thread
#define STACKSIZE 1024
#define PRIORITY 9

// Call once on startup
int display_init()
{
	display_dev = device_get_binding(CONFIG_LVGL_DISPLAY_DEV_NAME);
	if (display_dev == NULL) {
		LOG_ERR("display device not found");
		return -1;
	}

	k_mutex_init(&mutex1);

	LOG_INF("Display screen %s", log_strdup(CONFIG_LVGL_DISPLAY_DEV_NAME));

	// Icon (either MOABSYMBOL or the IEC Power Symbol)
	lv_style_copy(&icon_style, &lv_style_plain);
	icon_style.text.font = &moabsym_30;
	icon_label = lv_label_create(lv_scr_act(), NULL);
	lv_label_set_style(icon_label, LV_LABEL_STYLE_MAIN, &icon_style);
	lv_obj_set_width(icon_label, 32);
	lv_obj_align(icon_label, NULL, LV_ALIGN_IN_LEFT_MID, 2, 0);

	// Text Area
	lv_style_copy(&text_style, &lv_style_plain);
	text_style.text.font = &din2014_18;
	text_label = lv_label_create(lv_scr_act(), NULL);
	lv_label_set_style(text_label, LV_LABEL_STYLE_MAIN, &text_style);

	lv_obj_set_hidden(text_label, true);
	lv_obj_set_hidden(icon_label, true);

	display_big_text("PROJ MOAB");

	lv_task_handler();
	display_blanking_off(display_dev);

	return 0;
}


// Called by display update thread
// For: text with icon area
static void refresh_big_text_icon(our_fonts_t font_index)
{
	lv_label_long_mode_t longmode;

	lv_obj_set_hidden(text_label, true);
	lv_obj_set_hidden(icon_label, true);        // TODO: why was this false?

	// force redraw of entire screen
	// required because of lvgl or screen bug
	lv_obj_set_size(text_label, 128, 32);
	lv_obj_align(text_label, NULL, LV_ALIGN_CENTER, 0, 0);

    if (font_index == IECSYMBOL)
	    icon_style.text.font = &iecsymbol_30;
    else
	    icon_style.text.font = &moabsym_30;

	text_style.text.font = &din2014_18;

	lv_obj_set_hidden(icon_label, false);
	lv_obj_align(icon_label, NULL, LV_ALIGN_IN_LEFT_MID, 2, 0);
	longmode = lv_label_get_long_mode(text_label);
	if (longmode != LV_LABEL_LONG_BREAK)
	{
		lv_label_set_long_mode(text_label, LV_LABEL_LONG_BREAK);
		lv_obj_invalidate(text_label);
        // Another load-bearing poster
		k_sleep(50);
	}
	lv_obj_set_hidden(text_label, false);
	lv_label_set_align(text_label, LV_LABEL_ALIGN_LEFT);
	lv_label_set_long_mode(text_label, LV_LABEL_LONG_BREAK);
	lv_obj_set_width(text_label, 94);
	lv_obj_align(text_label, NULL, LV_ALIGN_IN_LEFT_MID, 36, 0);
}


// Called by display update thread
// For alerts and status messages
static void refresh_big_text_only(void)
{
	lv_obj_set_hidden(text_label, true);
	lv_obj_set_hidden(icon_label, true);

	// force redraw of entire screen
	// required because of lvgl or screen bug
	lv_obj_set_size(text_label, 128, 32);
	lv_obj_align(text_label, NULL, LV_ALIGN_CENTER, 0, 0);

	text_style.text.font = &din2014_18;

	lv_obj_set_hidden(icon_label, true);
	lv_obj_set_hidden(text_label, false);
	lv_label_set_align(text_label, LV_LABEL_ALIGN_CENTER);
	lv_label_set_long_mode(text_label, LV_LABEL_LONG_BREAK);
	lv_obj_set_size(text_label, 128, 32);
	lv_obj_align(text_label, NULL, LV_ALIGN_CENTER, 0, 0);

}


// Called by display update thread
// For: scrolling text
static void refresh_small_text(void)
{
	lv_obj_set_hidden(text_label, true);
	lv_obj_set_hidden(icon_label, true);

	// force redraw of entire screen
	// required because of lvgl or screen bug
	lv_obj_set_size(text_label, 128, 32);
	lv_obj_align(text_label, NULL, LV_ALIGN_CENTER, 0, 0);

	// For scrolling text we use a very small font
	text_style.text.font = &din2014light_12;

	lv_obj_set_hidden(icon_label, true);
	lv_obj_set_hidden(text_label, false);
	lv_label_set_align(text_label, LV_LABEL_ALIGN_CENTER);
	lv_label_set_long_mode(text_label, LV_LABEL_LONG_SROLL_CIRC);
	lv_obj_set_size(text_label, 128, 32);
	lv_obj_align(text_label, NULL, LV_ALIGN_CENTER, 0, 0);

}


void display_big_text_icon(const char *str, disp_icon_t i)
{
    // The icon is really a font, so convert number to a glyph
	static char icon_str[4] = {0};

	k_mutex_lock(&mutex1, K_FOREVER);
	lv_label_set_text(text_label, str);
	sprintf(icon_str, "%d", (u8_t) i);
	lv_label_set_text(icon_label, icon_str);
	k_mutex_unlock(&mutex1);

	refresh_big_text_icon(MOABSYMBOL);
}

void display_power_symbol(const char *str, disp_power_icon_t i)
{
    // The icon is really a font, so convert number to a glyph
	static char icon_str[4] = {0};

	k_mutex_lock(&mutex1, K_FOREVER);
	lv_label_set_text(text_label, str);
	sprintf(icon_str, "%d", (u8_t) i);
	lv_label_set_text(icon_label, icon_str);
	k_mutex_unlock(&mutex1);

	refresh_big_text_icon(IECSYMBOL);
}



void display_big_text(const char *str)
{
	k_mutex_lock(&mutex1, K_FOREVER);
	lv_label_set_text(text_label, str);
	k_mutex_unlock(&mutex1);

	refresh_big_text_only();
}


void display_small_text(const char *str)
{
	k_mutex_lock(&mutex1, K_FOREVER);
	lv_label_set_text(text_label, str);
	k_mutex_unlock(&mutex1);

	refresh_small_text();
}


static void disp_task(void)
{
	if (display_init()) {
		LOG_ERR("Failed to initalize display");
		return;
	}
	
	while(true)
	{
		lv_task_handler();
		k_sleep(5);
	}
}

K_THREAD_DEFINE(disp_task_id, STACKSIZE, disp_task, NULL, NULL, NULL, PRIORITY, 0, K_NO_WAIT);
