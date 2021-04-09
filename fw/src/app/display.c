// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "display.h"
#include "app_version.h"

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

lv_obj_t* s1;
lv_obj_t* s2;
lv_obj_t* s3;
lv_obj_t* s4;

lv_obj_t* i1;
lv_obj_t* i2;
lv_obj_t* t1;
lv_obj_t* t2;
lv_obj_t* t3;
lv_obj_t* t4;

static lv_style_t i1_style;      // moab_symbol 
static lv_style_t i2_style;      // power_symbol
static lv_style_t t1_style;      // big, offset 32
static lv_style_t t2_style;      // big, centered
static lv_style_t t3_style;      // small, centered, scrolling
static lv_style_t t4_style;      // big, offset 32 power_symbol

// For the display thread
#define STACKSIZE 1024*4
#define PRIORITY 9

// Call once on startup
int display_init()
{
    // Although the lvgl docs say to call lv_init()
    // It's already called by this point

    display_dev = device_get_binding(CONFIG_LVGL_DISPLAY_DEV_NAME);
    if (display_dev == NULL) {
        LOG_ERR("display device not found");
        return -1;
    }

    k_mutex_init(&mutex1);

    LOG_INF("Display screen %s", log_strdup(CONFIG_LVGL_DISPLAY_DEV_NAME));

    // SCREENS
    s1 = lv_obj_create(NULL, NULL);
    s2 = lv_obj_create(NULL, NULL);
    s3 = lv_obj_create(NULL, NULL);
    s4 = lv_obj_create(NULL, NULL);

    // STYLES
    lv_style_copy(&i1_style, &lv_style_plain);
    lv_style_copy(&i2_style, &lv_style_plain);
    lv_style_copy(&t1_style, &lv_style_plain);
    lv_style_copy(&t2_style, &lv_style_plain);
    lv_style_copy(&t3_style, &lv_style_plain);
    lv_style_copy(&t4_style, &lv_style_plain);

    i1_style.text.font = &moabsym_30;
    i2_style.text.font = &iecsymbol_30;
    t1_style.text.font = &din2014_18;
    t2_style.text.font = &din2014_18;
    t3_style.text.font = &din2014light_12;
    t4_style.text.font = &din2014_18;

    //
    // SCREEN1
    //
    i1 = lv_label_create(s1, NULL);
    lv_label_set_style(i1, LV_LABEL_STYLE_MAIN, &i1_style);
    lv_obj_set_width(i1, 32);
    lv_obj_align(i1, NULL, LV_ALIGN_IN_LEFT_MID, 2, 0);

    t1 = lv_label_create(s1, NULL);
    lv_label_set_style(t1, LV_LABEL_STYLE_MAIN, &t1_style);

    lv_label_set_long_mode(t1, LV_LABEL_LONG_BREAK);
    lv_label_set_align(t1,     LV_LABEL_ALIGN_LEFT);
    lv_label_set_text(t1, "TEXT1");
    lv_obj_set_width(t1, 94);
    lv_obj_align(t1, NULL, LV_ALIGN_IN_LEFT_MID, 36, 0);

    //
    // SCREEN2
    //
    t2 = lv_label_create(s2, NULL);
    lv_label_set_style(t2, LV_LABEL_STYLE_MAIN, &t2_style);
    lv_label_set_long_mode(t2, LV_LABEL_LONG_BREAK);
    lv_label_set_align(t2, LV_LABEL_ALIGN_CENTER);
    lv_obj_set_size(t2, 128, 32);
    lv_obj_align(t2, NULL, LV_ALIGN_CENTER, 0, 0);

    //
    // SCREEN3 (Small Text)
    //
    t3 = lv_label_create(s3, NULL);
    lv_label_set_style(t3, LV_LABEL_STYLE_MAIN, &t3_style);
    lv_label_set_long_mode(t3, LV_LABEL_LONG_BREAK);
    lv_label_set_align(t3, LV_LABEL_ALIGN_CENTER);
    lv_obj_set_size(t3, 128, 32);
    lv_obj_align(t3, NULL, LV_ALIGN_IN_TOP_MID, 0, 0);

    //
    // SCREEN4
    //
    i2 = lv_label_create(s4, NULL);
    lv_label_set_style(i2, LV_LABEL_STYLE_MAIN, &i2_style);
    lv_obj_set_width(i2, 32);
    lv_obj_align(i2, NULL, LV_ALIGN_IN_LEFT_MID, 2, 0);

    t4 = lv_label_create(s4, NULL);
    lv_label_set_style(t4, LV_LABEL_STYLE_MAIN, &t4_style);

    lv_label_set_long_mode(t4, LV_LABEL_LONG_BREAK);
    lv_label_set_align(t4,     LV_LABEL_ALIGN_LEFT);
    lv_label_set_text(t4, "TEXT1");
    lv_obj_set_width(t4, 94); //align text to label 
    lv_obj_align(t4, NULL, LV_ALIGN_IN_LEFT_MID, 36, 0);


    //LOG_INF("Version %s", log_strdup(APP_SEMVER));
    static char splash[30] = {0};
    sprintf(splash, "PROJECT  MOAB\n%s", APP_MAJORMINORPATCH);

    display_small_text(splash);

    lv_task_handler();
    display_blanking_off(display_dev);

    return 0;
}


// Four entry points, all called by main.c thread

void display_power_symbol(const char *str, disp_power_icon_t i)
{
    // The icon is really a font, so convert number to a glyph
    static char icon_str[4] = {0};
    k_mutex_lock(&mutex1, K_FOREVER);

    lv_label_set_text(t1, str);
    sprintf(icon_str, "%d", (u8_t) i);
    lv_label_set_text(i1, icon_str);
    lv_scr_load(s1);        // toggle IECSYMBOL

    k_mutex_unlock(&mutex1);
}



void display_big_text(const char *str)
{
    k_mutex_lock(&mutex1, K_FOREVER);

    lv_label_set_text(t2, str);
    lv_scr_load(s2);        // toggle IECSYMBOL

    k_mutex_unlock(&mutex1);
}

void display_big_text_icon(const char *str, disp_icon_t i)
{
    // The icon is really a font, so convert number to a glyph
    static char icon_str[4] = {0};

    k_mutex_lock(&mutex1, K_FOREVER);

    lv_label_set_text(t1, str);
    sprintf(icon_str, "%d", (u8_t) i);
    lv_label_set_text(i1, icon_str);
    lv_scr_load(s1); // toggle MOABSYMBOL

    k_mutex_unlock(&mutex1);
}

void display_small_text(const char *str)
{
    k_mutex_lock(&mutex1, K_FOREVER);

    lv_label_set_text(t3, str);
    lv_scr_load(s3);        // toggle IECSYMBOL

    k_mutex_unlock(&mutex1);
}

void display_big_text_power_icon(const char *str, disp_power_icon_t i)
{
    // The icon is really a font, so convert number to a glyph
    static char icon_str[4] = {0};

    k_mutex_lock(&mutex1, K_FOREVER);

    lv_label_set_text(t4, str);
    sprintf(icon_str, "%d", (u8_t) i);
    lv_label_set_text(i2, icon_str);
    lv_scr_load(s4); // toggle MOABSYMBOL

    k_mutex_unlock(&mutex1);
}

static void disp_task(void)
{
    if (display_init()) {
        LOG_ERR("Failed to initalize display");
        return;
    }
    
    while(true)
    {
        k_mutex_lock(&mutex1, K_FOREVER);
        lv_task_handler();
        k_mutex_unlock(&mutex1);

        lv_tick_inc(K_MSEC(5));
        k_sleep(5);
    }
}

K_THREAD_DEFINE(disp_task_id, STACKSIZE, disp_task, NULL, NULL, NULL, PRIORITY, 0, K_NO_WAIT);
