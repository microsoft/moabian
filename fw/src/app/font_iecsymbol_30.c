// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <lvgl.h>

/*******************************************************************************
 * Size: 30 px
 * Bpp: 1
 * Opts: 
 ******************************************************************************/

#ifndef  IECSYMBOL_30
#define  IECSYMBOL_30 1
#endif

#if  IECSYMBOL_30

/*-----------------
 *    BITMAPS
 *----------------*/

/*Store the image of the glyphs*/
static LV_ATTRIBUTE_LARGE_CONST const uint8_t gylph_bitmap[] = {
    // "1" maps to this glyph
    /* U+23FB "⏻" */
    0x0, 0x18, 0x0, 0x0, 0x1e, 0x0, 0x0, 0xf,
    0x0, 0x0, 0x7, 0x80, 0x0, 0x3, 0xc0, 0x0,
    0x1, 0xe0, 0x0, 0x0, 0xf0, 0x0, 0x38, 0x78,
    0x38, 0x3e, 0x3c, 0x3c, 0x1f, 0x1e, 0x1f, 0x1f,
    0xf, 0xf, 0xcf, 0x7, 0x83, 0xef, 0x83, 0xc0,
    0xf7, 0x81, 0xe0, 0x7f, 0xc0, 0xf0, 0x1f, 0xe0,
    0x78, 0xf, 0xf0, 0x3c, 0x7, 0xf8, 0xc, 0x3,
    0xfc, 0x0, 0x1, 0xff, 0x0, 0x1, 0xf7, 0x80,
    0x0, 0xf3, 0xe0, 0x0, 0xf8, 0xf0, 0x0, 0x78,
    0x7e, 0x0, 0xfc, 0x1f, 0xc1, 0xfc, 0x7, 0xff,
    0xfc, 0x1, 0xff, 0xfc, 0x0, 0x3f, 0xf8, 0x0,
    0x7, 0xf0, 0x0,

    // "2"...
    /* U+23FC "⏼" */
    0x0, 0x3f, 0x80, 0x0, 0x1f, 0xff, 0x0, 0x3,
    0xff, 0xfc, 0x0, 0x7f, 0xff, 0xe0, 0xf, 0xff,
    0xff, 0x1, 0xfe, 0x7, 0xf8, 0x3f, 0x80, 0x1f,
    0xc3, 0xf0, 0x0, 0xfc, 0x7e, 0xe, 0x7, 0xe7,
    0xc1, 0xf0, 0x3e, 0xfc, 0x1f, 0x3, 0xff, 0x81,
    0xf0, 0x1f, 0xf8, 0x1f, 0x1, 0xff, 0x81, 0xf0,
    0x1f, 0xf8, 0x1f, 0x1, 0xff, 0x81, 0xf0, 0x1f,
    0xf8, 0x1f, 0x1, 0xff, 0xc1, 0xf0, 0x3f, 0x7c,
    0x1f, 0x3, 0xe7, 0xe1, 0xf0, 0x7e, 0x3f, 0xe,
    0xf, 0xc3, 0xf8, 0x1, 0xfc, 0x1f, 0xe0, 0x7f,
    0x80, 0xff, 0xff, 0xf0, 0x7, 0xff, 0xfe, 0x0,
    0x3f, 0xff, 0xc0, 0x0, 0xff, 0xf0, 0x0, 0x3,
    0xfc, 0x0,

    /* U+23FD "⏽" */
    0x77, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xfe, 0xe0,

    /* U+23FE "⏾" */
    0x1, 0x0, 0x0, 0x60, 0x0, 0xe, 0x0, 0x1,
    0xe0, 0x0, 0x1c, 0x0, 0x3, 0xc0, 0x0, 0x7c,
    0x0, 0x7, 0xc0, 0x0, 0x7c, 0x0, 0xf, 0xc0,
    0x0, 0xfc, 0x0, 0xf, 0xc0, 0x0, 0xfe, 0x0,
    0xf, 0xe0, 0x0, 0xfe, 0x0, 0xf, 0xf0, 0x0,
    0xff, 0x0, 0x7, 0xf8, 0x0, 0x7f, 0x80, 0x3,
    0xfc, 0x0, 0x3f, 0xe0, 0x1, 0xff, 0x0, 0xf,
    0xf8, 0x0, 0x7f, 0xc0, 0x3, 0xff, 0x0, 0xf,
    0xfc, 0x0, 0x3f, 0xe0,

    /* U+2B58 "⭘" */
    0x0, 0x3f, 0x80, 0x0, 0x3f, 0xfe, 0x0, 0xf,
    0xff, 0xe0, 0x7, 0xff, 0xff, 0x1, 0xfe, 0xf,
    0xf0, 0x3f, 0x0, 0x7e, 0xf, 0xc0, 0x7, 0xe3,
    0xf0, 0x0, 0x7e, 0x7c, 0x0, 0x7, 0xcf, 0x80,
    0x0, 0xfb, 0xe0, 0x0, 0xf, 0xfc, 0x0, 0x1,
    0xff, 0x80, 0x0, 0x3f, 0xf0, 0x0, 0x7, 0xfe,
    0x0, 0x0, 0xff, 0xc0, 0x0, 0x1f, 0xf8, 0x0,
    0x3, 0xef, 0x80, 0x0, 0xf9, 0xf0, 0x0, 0x1f,
    0x3f, 0x0, 0x7, 0xe3, 0xf0, 0x1, 0xf8, 0x3f,
    0x0, 0x7e, 0x7, 0xf8, 0x3f, 0xc0, 0x7f, 0xff,
    0xf0, 0x3, 0xff, 0xf8, 0x0, 0x3f, 0xfe, 0x0,
    0x0, 0xfe, 0x0, 0x0
};


/*---------------------
 *  GLYPH DESCRIPTION
 *--------------------*/

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {
    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */,
    {.bitmap_index = 0, .adv_w = 480, .box_w = 25, .box_h = 29, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 91, .adv_w = 480, .box_w = 28, .box_h = 28, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 189, .adv_w = 480, .box_w = 5, .box_h = 28, .ofs_x = 12, .ofs_y = 0},
    {.bitmap_index = 207, .adv_w = 480, .box_w = 20, .box_h = 27, .ofs_x = 4, .ofs_y = 0},
    {.bitmap_index = 275, .adv_w = 480, .box_w = 27, .box_h = 27, .ofs_x = 1, .ofs_y = 0}
};

/*---------------------
 *  CHARACTER MAPPING
 *--------------------*/


/*Collect the unicode lists and glyph_id offsets*/
static const lv_font_fmt_txt_cmap_t cmaps[] =
{
    {
        .range_start = 49, .range_length = 5, .glyph_id_start = 1,
        .unicode_list = NULL, .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY
    }
};



/*--------------------
 *  ALL CUSTOM DATA
 *--------------------*/

/*Store all the custom data of the font*/
static lv_font_fmt_txt_dsc_t font_dsc = {
    .glyph_bitmap = gylph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = NULL,
    .kern_scale = 0,
    .cmap_num = 1,
    .bpp = 1,
    .kern_classes = 0,
    .bitmap_format = 0
};


/*-----------------
 *  PUBLIC FONT
 *----------------*/

/*Initialize a public general font descriptor*/
lv_font_t  iecsymbol_30 = {
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,    /*Function pointer to get glyph's data*/
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,    /*Function pointer to get glyph's bitmap*/
    .line_height = 29,          /*The maximum line height required by the font*/
    .base_line = 0,             /*Baseline measured from the bottom of the line*/
#if !(LVGL_VERSION_MAJOR == 6 && LVGL_VERSION_MINOR == 0)
    .subpx = LV_FONT_SUBPX_NONE,
#endif
#if LV_VERSION_CHECK(7, 4, 0)
    .underline_position = 0,
    .underline_thickness = 0,
#endif
    .dsc = &font_dsc           /*The custom font data. Will be accessed by `get_glyph_bitmap/dsc` */
};



#endif /*#if  IECSYMBOL_30*/

