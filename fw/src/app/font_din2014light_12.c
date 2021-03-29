// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <lvgl.h>

/*******************************************************************************
 * Size: 12 px
 * Bpp: 1
 * Opts: 
 ******************************************************************************/

#ifndef DIN2014LIGHT_12
#define DIN2014LIGHT_12 1
#endif

#if DIN2014LIGHT_12

/*-----------------
 *    BITMAPS
 *----------------*/

/*Store the image of the glyphs*/
static LV_ATTRIBUTE_LARGE_CONST const uint8_t gylph_bitmap[] = {
    /* U+20 " " */
    0x0,

    /* U+21 "!" */
    0xfd,

    /* U+22 "\"" */
    0xf0,

    /* U+23 "#" */
    0x24, 0x4b, 0xfa, 0x44, 0x9f, 0x92, 0x28,

    /* U+24 "$" */
    0x21, 0x1d, 0x4a, 0x30, 0xe5, 0xaf, 0x88, 0x40,

    /* U+25 "%" */
    0xf4, 0x98, 0x98, 0x68, 0x16, 0x19, 0x29, 0x2f,

    /* U+26 "&" */
    0x70, 0xa1, 0x41, 0x6, 0x52, 0xa2, 0x3a,

    /* U+27 "'" */
    0xc0,

    /* U+28 "(" */
    0xa, 0x49, 0x24, 0x91, 0x0,

    /* U+29 ")" */
    0x8, 0x92, 0x49, 0x25, 0x0,

    /* U+2A "*" */
    0x23, 0x9c, 0x40,

    /* U+2B "+" */
    0x27, 0xc8, 0x40,

    /* U+2C "," */
    0xc0,

    /* U+2D "-" */
    0xe0,

    /* U+2E "." */
    0x80,

    /* U+2F "/" */
    0x11, 0x22, 0x24, 0x48, 0x88, 0x80,

    /* U+30 "0" */
    0x74, 0x63, 0x18, 0xc6, 0x2e,

    /* U+31 "1" */
    0xd5, 0x55,

    /* U+32 "2" */
    0x74, 0x42, 0x31, 0x11, 0x1f,

    /* U+33 "3" */
    0x74, 0x42, 0x61, 0x86, 0x2e,

    /* U+34 "4" */
    0x10, 0x82, 0x12, 0x49, 0x2f, 0xc2,

    /* U+35 "5" */
    0xfc, 0x3d, 0x10, 0x86, 0x2e,

    /* U+36 "6" */
    0x21, 0x10, 0xe8, 0xc6, 0x2e,

    /* U+37 "7" */
    0xfc, 0x84, 0x22, 0x10, 0x88,

    /* U+38 "8" */
    0x74, 0x62, 0xe8, 0xc6, 0x2e,

    /* U+39 "9" */
    0x74, 0x63, 0x17, 0x8, 0x84,

    /* U+3A ":" */
    0x84,

    /* U+3B ";" */
    0x86,

    /* U+3C "<" */
    0x3, 0xc4, 0x30,

    /* U+3D "=" */
    0xf0, 0xf0,

    /* U+3E ">" */
    0xc, 0x32, 0xc0,

    /* U+3F "?" */
    0x74, 0x42, 0x33, 0x10, 0x4,

    /* U+40 "@" */
    0x1e, 0x18, 0x65, 0xe6, 0x49, 0x92, 0x64, 0x98,
    0xd9, 0x0, 0x61, 0x7, 0x80,

    /* U+41 "A" */
    0x10, 0xc2, 0x92, 0x49, 0xf8, 0x61,

    /* U+42 "B" */
    0xf2, 0x28, 0xbc, 0x8e, 0x18, 0x7e,

    /* U+43 "C" */
    0x7a, 0x18, 0x20, 0x82, 0x8, 0x5e,

    /* U+44 "D" */
    0xfa, 0x18, 0x61, 0x86, 0x18, 0x7e,

    /* U+45 "E" */
    0xfc, 0x21, 0xf8, 0x42, 0x1f,

    /* U+46 "F" */
    0xfc, 0x21, 0xf8, 0x42, 0x10,

    /* U+47 "G" */
    0x7a, 0x18, 0x60, 0x9e, 0x18, 0x5e,

    /* U+48 "H" */
    0x86, 0x18, 0x7f, 0x86, 0x18, 0x61,

    /* U+49 "I" */
    0xff,

    /* U+4A "J" */
    0x8, 0x42, 0x10, 0x84, 0x3e,

    /* U+4B "K" */
    0x85, 0x12, 0x45, 0xd, 0x11, 0x22, 0x42,

    /* U+4C "L" */
    0x84, 0x21, 0x8, 0x42, 0x1f,

    /* U+4D "M" */
    0x83, 0x8f, 0x1d, 0x5a, 0xb2, 0x60, 0xc1,

    /* U+4E "N" */
    0x87, 0x1c, 0x69, 0x96, 0x58, 0xe1,

    /* U+4F "O" */
    0x7a, 0x18, 0x61, 0x86, 0x18, 0x5e,

    /* U+50 "P" */
    0xfa, 0x18, 0x61, 0xfa, 0x8, 0x20,

    /* U+51 "Q" */
    0x79, 0xa, 0x14, 0x28, 0x52, 0xa2, 0x3e,

    /* U+52 "R" */
    0xfa, 0x18, 0x61, 0xfa, 0x28, 0xa1,

    /* U+53 "S" */
    0x7a, 0x8, 0x10, 0x38, 0x18, 0x5e,

    /* U+54 "T" */
    0xfe, 0x20, 0x40, 0x81, 0x2, 0x4, 0x8,

    /* U+55 "U" */
    0x86, 0x18, 0x61, 0x86, 0x18, 0x5e,

    /* U+56 "V" */
    0x83, 0x9, 0x12, 0x42, 0x85, 0xc, 0x8,

    /* U+57 "W" */
    0x88, 0x63, 0x28, 0xc9, 0x52, 0x52, 0x94, 0xc6,
    0x30, 0x84,

    /* U+58 "X" */
    0x45, 0x22, 0x84, 0x30, 0xa4, 0xa1,

    /* U+59 "Y" */
    0x84, 0x88, 0xa1, 0x41, 0x2, 0x4, 0x8,

    /* U+5A "Z" */
    0xfc, 0x21, 0x4, 0x21, 0x4, 0x3f,

    /* U+5B "[" */
    0xea, 0xaa, 0xb0,

    /* U+5C "\\" */
    0x82, 0x10, 0x82, 0x10, 0x82, 0x10, 0x42,

    /* U+5D "]" */
    0xd5, 0x55, 0x70,

    /* U+5E "^" */
    0x22, 0xa2,

    /* U+5F "_" */
    0xfc
};


/*---------------------
 *  GLYPH DESCRIPTION
 *--------------------*/

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {
    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */,
    {.bitmap_index = 0, .adv_w = 48, .box_w = 1, .box_h = 1, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1, .adv_w = 40, .box_w = 1, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 2, .adv_w = 56, .box_w = 2, .box_h = 2, .ofs_x = 1, .ofs_y = 6},
    {.bitmap_index = 3, .adv_w = 111, .box_w = 7, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 10, .adv_w = 94, .box_w = 5, .box_h = 12, .ofs_x = 1, .ofs_y = -2},
    {.bitmap_index = 18, .adv_w = 138, .box_w = 8, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 26, .adv_w = 125, .box_w = 7, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 33, .adv_w = 29, .box_w = 1, .box_h = 2, .ofs_x = 1, .ofs_y = 6},
    {.bitmap_index = 34, .adv_w = 58, .box_w = 3, .box_h = 11, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 39, .adv_w = 58, .box_w = 3, .box_h = 11, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 44, .adv_w = 83, .box_w = 5, .box_h = 4, .ofs_x = 0, .ofs_y = 4},
    {.bitmap_index = 47, .adv_w = 94, .box_w = 5, .box_h = 4, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 50, .adv_w = 38, .box_w = 1, .box_h = 2, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 51, .adv_w = 59, .box_w = 3, .box_h = 1, .ofs_x = 0, .ofs_y = 3},
    {.bitmap_index = 52, .adv_w = 41, .box_w = 1, .box_h = 1, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 53, .adv_w = 89, .box_w = 4, .box_h = 11, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 59, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 64, .adv_w = 94, .box_w = 2, .box_h = 8, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 66, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 71, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 76, .adv_w = 94, .box_w = 6, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 82, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 87, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 92, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 97, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 102, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 107, .adv_w = 38, .box_w = 1, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 108, .adv_w = 38, .box_w = 1, .box_h = 7, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 109, .adv_w = 83, .box_w = 4, .box_h = 5, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 112, .adv_w = 94, .box_w = 4, .box_h = 3, .ofs_x = 1, .ofs_y = 3},
    {.bitmap_index = 114, .adv_w = 83, .box_w = 4, .box_h = 5, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 117, .adv_w = 94, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 122, .adv_w = 172, .box_w = 10, .box_h = 10, .ofs_x = 1, .ofs_y = -2},
    {.bitmap_index = 135, .adv_w = 106, .box_w = 6, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 141, .adv_w = 114, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 147, .adv_w = 111, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 153, .adv_w = 116, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 159, .adv_w = 104, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 164, .adv_w = 103, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 169, .adv_w = 116, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 175, .adv_w = 122, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 181, .adv_w = 50, .box_w = 1, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 182, .adv_w = 97, .box_w = 5, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 187, .adv_w = 119, .box_w = 7, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 194, .adv_w = 96, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 199, .adv_w = 144, .box_w = 7, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 206, .adv_w = 122, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 212, .adv_w = 115, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 218, .adv_w = 113, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 224, .adv_w = 115, .box_w = 7, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 231, .adv_w = 116, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 237, .adv_w = 109, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 243, .adv_w = 99, .box_w = 7, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 250, .adv_w = 129, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 256, .adv_w = 110, .box_w = 7, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 263, .adv_w = 157, .box_w = 10, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 273, .adv_w = 106, .box_w = 6, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 279, .adv_w = 103, .box_w = 7, .box_h = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 286, .adv_w = 99, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 292, .adv_w = 59, .box_w = 2, .box_h = 10, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 295, .adv_w = 89, .box_w = 5, .box_h = 11, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 302, .adv_w = 59, .box_w = 2, .box_h = 10, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 305, .adv_w = 87, .box_w = 5, .box_h = 3, .ofs_x = 0, .ofs_y = 5},
    {.bitmap_index = 307, .adv_w = 101, .box_w = 6, .box_h = 1, .ofs_x = 0, .ofs_y = -2}
};

/*---------------------
 *  CHARACTER MAPPING
 *--------------------*/



/*Collect the unicode lists and glyph_id offsets*/
static const lv_font_fmt_txt_cmap_t cmaps[] =
{
    {
        .range_start = 32, .range_length = 64, .glyph_id_start = 1,
        .unicode_list = NULL, .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY
    }
};

/*-----------------
 *    KERNING
 *----------------*/


/*Map glyph_ids to kern left classes*/
static const uint8_t kern_left_class_mapping[] =
{
    0, 1, 0, 2, 0, 0, 0, 0,
    2, 3, 0, 4, 0, 5, 6, 5,
    0, 0, 0, 0, 0, 0, 0, 0,
    7, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 8, 9, 10, 11, 0, 12,
    13, 0, 0, 14, 15, 16, 0, 0,
    17, 18, 19, 20, 21, 22, 23, 24,
    25, 26, 27, 28, 3, 0, 0, 0,
    0
};

/*Map glyph_ids to kern right classes*/
static const uint8_t kern_right_class_mapping[] =
{
    0, 0, 0, 1, 0, 0, 0, 0,
    1, 0, 2, 3, 0, 4, 5, 4,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 6, 0, 7, 0, 0, 0,
    7, 0, 0, 8, 0, 0, 0, 0,
    7, 0, 9, 0, 10, 11, 12, 13,
    14, 15, 16, 17, 0, 0, 2, 0,
    0
};

/*Kern values between classes*/
static const int8_t kern_class_values[] =
{
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -6, -3, -9, -4,
    -10, -4, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 0, 0, -2, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, -6, -1,
    -7, 0, -12, 0, 0, 0, 0, 0,
    0, -2, 0, 0, -6, 0, -5, 0,
    -5, 0, -4, -1, -4, 0, -11, 0,
    -9, -4, 0, -9, 0, -3, -2, -1,
    -4, 0, -2, 0, -8, 0, 0, -8,
    0, -3, -2, -4, -6, -2, 0, 0,
    0, -5, -3, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, -9,
    0, -7, 0, -2, 0, -1, 0, -1,
    -1, -7, -2, -7, -1, 0, -9, 0,
    0, 0, 0, 0, 0, 0, 0, -2,
    0, 0, -2, 0, 0, 0, -1, 0,
    0, 0, 0, 0, -1, 0, -2, 0,
    -3, 0, -1, -2, 0, -2, 0, -4,
    -3, 0, -4, 0, 0, -4, 0, -1,
    0, -2, 0, 0, -2, 0, -2, 0,
    -3, -5, -1, 0, 0, 0, -8, 0,
    -8, -2, -19, -2, -3, -1, 0, -2,
    -1, -7, -3, -3, 0, 0, 0, 0,
    0, -1, 0, -3, 0, 0, 0, 0,
    -1, 0, -3, -3, -2, 0, 0, 0,
    0, 0, -4, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, -1, 0,
    -4, 0, -5, 0, -2, 0, -2, -2,
    -2, -1, -2, 0, 0, -3, 0, -9,
    0, -10, 0, -8, 1, -6, 0, -6,
    -2, -10, 0, -12, -6, 0, -15, 0,
    -4, 0, 0, -4, 0, -1, 0, -5,
    0, 0, -2, 0, -2, 0, -3, -5,
    -1, -1, -1, 0, -11, -1, -11, -1,
    -24, -1, -1, -1, 0, 0, 0, -6,
    -4, -4, -4, 0, 0, -4, 0, 0,
    0, -1, 0, 0, -2, 0, -2, 0,
    -3, -5, -1, -1, 0, 0, 0, -1,
    0, 0, -2, 0, 0, -2, 0, -2,
    0, 0, -4, 0, 0, 0, 0, 0,
    0, 0, 0, -2, 0, 0, -4, 0,
    -2, 0, -2, -5, 0, 0, 0, 0,
    -11, -6, -7, -2, -18, -2, -2, 1,
    0, 0, 0, -2, 0, 0, 0, 0,
    0, 0, 0, -2, 0, -5, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -9, -3, -7, -2, -13, -2,
    -1, 0, 0, 0, 0, -1, 0, 0,
    0, 0, 0, -4, -2, -1, 0, -8,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -2, 0, -4, 0, -3,
    -2, -3, 0, -2, 0, -1, 0, -1,
    -2, 0, 0, 0, 0, -9, -6, -9,
    -5, -18, -5, -3, 0, 0, 0, 0,
    -2, 0, 0, 0, 0, 0, 0, -5,
    0, -3, -2, -3, 0, 0, 0, 0,
    0, -1, 0, 0
};


/*Collect the kern class' data in one place*/
static const lv_font_fmt_txt_kern_classes_t kern_classes =
{
    .class_pair_values   = kern_class_values,
    .left_class_mapping  = kern_left_class_mapping,
    .right_class_mapping = kern_right_class_mapping,
    .left_class_cnt      = 28,
    .right_class_cnt     = 17,
};

/*--------------------
 *  ALL CUSTOM DATA
 *--------------------*/

/*Store all the custom data of the font*/
static lv_font_fmt_txt_dsc_t font_dsc = {
    .glyph_bitmap = gylph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = &kern_classes,
    .kern_scale = 16,
    .cmap_num = 1,
    .bpp = 1,
    .kern_classes = 1,
    .bitmap_format = 0
};


/*-----------------
 *  PUBLIC FONT
 *----------------*/

/*Initialize a public general font descriptor*/
lv_font_t din2014light_12 = {
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,    /*Function pointer to get glyph's data*/
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,    /*Function pointer to get glyph's bitmap*/
    .line_height = 12,          /*The maximum line height required by the font*/
    .base_line = 2,             /*Baseline measured from the bottom of the line*/
#if !(LVGL_VERSION_MAJOR == 6 && LVGL_VERSION_MINOR == 0)
    .subpx = LV_FONT_SUBPX_NONE,
#endif
    .dsc = &font_dsc           /*The custom font data. Will be accessed by `get_glyph_bitmap/dsc` */
};

#endif /*#if DIN2014LIGHT_12*/

