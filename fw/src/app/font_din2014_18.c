// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <lvgl.h>

/*******************************************************************************
 * Size: 18 px
 * Bpp: 1
 * Opts: 
 ******************************************************************************/

#ifndef DIN2014_18
#define DIN2014_18 1
#endif

#if DIN2014_18

/*-----------------
 *    BITMAPS
 *----------------*/

/*Store the image of the glyphs*/
static LV_ATTRIBUTE_LARGE_CONST const uint8_t gylph_bitmap[] = {
    /* U+20 " " */

    /* U+21 "!" */
    0x9f, 0xff, 0xff, 0xfa, 0x7e,

    /* U+22 "\"" */
    0x1, 0xb6, 0xdb,

    /* U+23 "#" */
    0x0, 0x3, 0xb8, 0x66, 0xc, 0xc7, 0xfe, 0xff,
    0xce, 0xe1, 0xdc, 0xff, 0xcf, 0xf8, 0xcc, 0x3b,
    0x87, 0x70,

    /* U+24 "$" */
    0x8, 0x3, 0x0, 0xc0, 0xfc, 0x7f, 0x9b, 0x46,
    0xc1, 0xf0, 0x3f, 0x7, 0xe0, 0xf8, 0x36, 0x6f,
    0x9f, 0xe3, 0xf0, 0x30, 0xc, 0x0,

    /* U+25 "%" */
    0x0, 0x1, 0xe1, 0x8e, 0xcc, 0x33, 0x70, 0xcd,
    0x81, 0xfe, 0x3, 0xb0, 0x1, 0xde, 0x6, 0xd8,
    0x33, 0x60, 0xcd, 0x86, 0x36, 0x38, 0x78, 0x0,
    0x0,

    /* U+26 "&" */
    0x0, 0x3, 0xf0, 0x33, 0x3, 0x30, 0x3f, 0x3,
    0xe0, 0x3c, 0x7, 0xee, 0x67, 0xe6, 0x3c, 0x73,
    0xc7, 0xfc, 0x3f, 0xe0, 0x0,

    /* U+27 "'" */
    0xd, 0xb0,

    /* U+28 "(" */
    0x1, 0x9d, 0xce, 0x73, 0x9c, 0xe7, 0x39, 0xce,
    0x71, 0xce, 0x30,

    /* U+29 ")" */
    0x3, 0x1c, 0x73, 0x9c, 0xe7, 0x39, 0xce, 0x73,
    0x9d, 0xce, 0x60,

    /* U+2A "*" */
    0x0, 0x31, 0xf9, 0xe7, 0xeb, 0x84, 0x0,

    /* U+2B "+" */
    0x10, 0x70, 0xe7, 0xff, 0xe7, 0xe, 0x0,

    /* U+2C "," */
    0xdf, 0xfd, 0x0,

    /* U+2D "-" */
    0x1, 0xe7, 0x80,

    /* U+2E "." */
    0xff, 0x80,

    /* U+2F "/" */
    0x0, 0x7, 0x6, 0x6, 0xc, 0xc, 0xc, 0x18,
    0x18, 0x18, 0x30, 0x30, 0x70, 0x60, 0x60, 0xe0,
    0xc0,

    /* U+30 "0" */
    0x0, 0x1f, 0x9f, 0xee, 0x76, 0x3b, 0x1d, 0x8e,
    0xc7, 0x63, 0xb1, 0xdc, 0xef, 0xe3, 0xe0, 0x0,

    /* U+31 "1" */
    0x3, 0xff, 0xf3, 0x9c, 0xe7, 0x39, 0xce, 0x73,
    0x80,

    /* U+32 "2" */
    0x0, 0x7e, 0xfe, 0xc7, 0x7, 0x6, 0xe, 0x1c,
    0x38, 0x70, 0x70, 0xff, 0xff,

    /* U+33 "3" */
    0x0, 0x1f, 0x9f, 0xcc, 0x70, 0x30, 0x38, 0x78,
    0x1e, 0x3, 0x81, 0xd8, 0xef, 0xe3, 0xe0, 0x0,

    /* U+34 "4" */
    0x0, 0x3, 0x81, 0xc0, 0x70, 0x38, 0xe, 0x3,
    0xb1, 0xcc, 0x73, 0x3f, 0xef, 0xf8, 0xc, 0x3,
    0x0,

    /* U+35 "5" */
    0x0, 0xff, 0xfe, 0xe0, 0xe8, 0xfe, 0xff, 0x47,
    0x7, 0x7, 0xe7, 0x7e, 0x3c, 0x0,

    /* U+36 "6" */
    0x0, 0x7, 0x7, 0x3, 0x83, 0x81, 0xc1, 0xfc,
    0xff, 0x63, 0xb1, 0xdc, 0xef, 0xe3, 0xe0, 0x0,

    /* U+37 "7" */
    0x0, 0xff, 0xff, 0xc6, 0xc6, 0xe, 0xc, 0xc,
    0x1c, 0x18, 0x38, 0x38, 0x30,

    /* U+38 "8" */
    0x0, 0x1f, 0x9f, 0xee, 0x76, 0x3b, 0xb8, 0xfc,
    0xfe, 0x63, 0xb1, 0xdc, 0xef, 0xe3, 0xe0, 0x0,

    /* U+39 "9" */
    0x0, 0x1f, 0x9f, 0xec, 0x76, 0x3b, 0x9d, 0xfe,
    0x7e, 0x7, 0x7, 0x3, 0x83, 0x81, 0xc0,

    /* U+3A ":" */
    0xff, 0x0, 0x27, 0xe0,

    /* U+3B ";" */
    0xff, 0x0, 0x27, 0xff, 0x40,

    /* U+3C "<" */
    0x0, 0xc, 0x79, 0xe7, 0xf, 0xf, 0x87, 0x6,

    /* U+3D "=" */
    0x0, 0xff, 0x7e, 0x0, 0xff, 0x7e,

    /* U+3E ">" */
    0x3, 0xe, 0x1e, 0x3c, 0xff, 0xb8, 0x80,

    /* U+3F "?" */
    0x0, 0x1f, 0x1f, 0xcc, 0x60, 0x30, 0x38, 0x38,
    0x38, 0x1c, 0x4, 0x4, 0x3, 0x81, 0xc0,

    /* U+40 "@" */
    0x0, 0x0, 0x7, 0xf0, 0x1f, 0xf8, 0x38, 0x1c,
    0x73, 0xee, 0x67, 0xf6, 0x66, 0x77, 0x66, 0x77,
    0x66, 0x77, 0x66, 0x76, 0x67, 0xfe, 0x73, 0x9c,
    0x38, 0x0, 0x1f, 0xf8, 0xf, 0xf0, 0x0, 0x0,

    /* U+41 "A" */
    0x0, 0x1, 0xc0, 0x38, 0xf, 0x81, 0xf0, 0x36,
    0xe, 0xe1, 0x8c, 0x7b, 0x8f, 0xf9, 0xff, 0x70,
    0x6e, 0xe,

    /* U+42 "B" */
    0x0, 0x3f, 0xcf, 0xfb, 0x8e, 0xe3, 0xb9, 0xcf,
    0xf3, 0xfe, 0xe1, 0xb8, 0x6e, 0x3b, 0xfe, 0xfe,
    0x0,

    /* U+43 "C" */
    0x0, 0x7, 0xf0, 0xff, 0x38, 0xe7, 0xc, 0xc0,
    0x18, 0x3, 0x0, 0x70, 0xe, 0x19, 0xc7, 0x1f,
    0xc1, 0xf0, 0x0, 0x0,

    /* U+44 "D" */
    0x0, 0x3f, 0xcf, 0xfb, 0x8e, 0xe1, 0xb8, 0x6e,
    0x1f, 0x86, 0xe1, 0xb8, 0x6e, 0x3b, 0xfc, 0xfe,
    0x0,

    /* U+45 "E" */
    0x0, 0xff, 0xff, 0xe0, 0xe0, 0xe0, 0xff, 0xfe,
    0xe0, 0xe0, 0xe0, 0xff, 0xff,

    /* U+46 "F" */
    0x0, 0xff, 0xff, 0xe0, 0xe0, 0xe0, 0xff, 0xff,
    0xe0, 0xe0, 0xe0, 0xe0, 0xe0,

    /* U+47 "G" */
    0x0, 0x3, 0xf0, 0xff, 0x38, 0xe7, 0xc, 0xc0,
    0x18, 0x3, 0x1e, 0x73, 0xce, 0x19, 0xc7, 0x1f,
    0xc1, 0xf0, 0x0, 0x0,

    /* U+48 "H" */
    0x1, 0x38, 0x7e, 0x1f, 0x87, 0xe1, 0xf8, 0x7f,
    0xff, 0xff, 0xe1, 0xf8, 0x7e, 0x1f, 0x87, 0xe1,
    0xc0,

    /* U+49 "I" */
    0x1f, 0xff, 0xff, 0xff, 0xfe,

    /* U+4A "J" */
    0x0, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7,
    0x7, 0x7, 0x47, 0xfe, 0x7c, 0x0,

    /* U+4B "K" */
    0x0, 0x1c, 0x73, 0x9c, 0x77, 0xe, 0xe1, 0xf8,
    0x3f, 0x7, 0xf0, 0xf7, 0x1c, 0xe3, 0x8e, 0x71,
    0xee, 0x1c,

    /* U+4C "L" */
    0x0, 0xe0, 0xe0, 0xe0, 0xe0, 0xe0, 0xe0, 0xe0,
    0xe0, 0xe0, 0xe0, 0xff, 0xff,

    /* U+4D "M" */
    0x0, 0xe, 0x7, 0xf0, 0xff, 0xf, 0xf9, 0xff,
    0x9f, 0xff, 0xfe, 0xf7, 0xef, 0x7e, 0x67, 0xe6,
    0x7e, 0x7, 0xe0, 0x70,

    /* U+4E "N" */
    0x0, 0x38, 0x7f, 0x1f, 0xc7, 0xf9, 0xfe, 0x7f,
    0xdf, 0xbf, 0xe7, 0xf9, 0xfe, 0x3f, 0x8f, 0xe1,
    0xc0,

    /* U+4F "O" */
    0x0, 0x7, 0xf0, 0xff, 0x38, 0xe7, 0xc, 0xc1,
    0x98, 0x3b, 0x6, 0x70, 0xce, 0x19, 0xc7, 0x1f,
    0xc1, 0xf0, 0x0, 0x0,

    /* U+50 "P" */
    0x0, 0x3f, 0xcf, 0xfb, 0x8e, 0xe1, 0xb8, 0x6e,
    0x7b, 0xfc, 0xfc, 0x38, 0xe, 0x3, 0x80, 0xe0,
    0x0,

    /* U+51 "Q" */
    0x0, 0x3, 0xf8, 0x3f, 0xc7, 0x1c, 0x70, 0xc6,
    0xc, 0x60, 0xe6, 0xc, 0x73, 0xc7, 0x3c, 0x73,
    0xc3, 0xfe, 0x1f, 0x60, 0x0,

    /* U+52 "R" */
    0x0, 0x3f, 0xcf, 0xfb, 0x86, 0xe1, 0xb8, 0xef,
    0xfb, 0xfc, 0xe7, 0x39, 0xce, 0x3b, 0x8e, 0xe1,
    0xc0,

    /* U+53 "S" */
    0x0, 0xf, 0xc7, 0xf9, 0xc4, 0x70, 0x1e, 0x3,
    0xf0, 0x3e, 0x3, 0xc0, 0x76, 0x1d, 0xfe, 0x3f,
    0x0, 0x0,

    /* U+54 "T" */
    0x0, 0x3f, 0xff, 0xf8, 0x70, 0x1c, 0x7, 0x1,
    0xc0, 0x70, 0x1c, 0x7, 0x1, 0xc0, 0x70, 0x1c,
    0x0,

    /* U+55 "U" */
    0x0, 0x38, 0x7e, 0x1f, 0x87, 0xe1, 0xf8, 0x7e,
    0x1f, 0x87, 0xe1, 0xf8, 0x77, 0x39, 0xfe, 0x3f,
    0x0, 0x0,

    /* U+56 "V" */
    0x0, 0x1c, 0x1d, 0x83, 0x38, 0xe7, 0x1c, 0x63,
    0xe, 0xe1, 0xdc, 0x1f, 0x3, 0xe0, 0x3c, 0x7,
    0x0, 0xe0,

    /* U+57 "W" */
    0x0, 0x0, 0xe1, 0x87, 0x63, 0xc6, 0x63, 0xc6,
    0x73, 0xce, 0x77, 0xee, 0x76, 0x6e, 0x36, 0x6c,
    0x3e, 0x7c, 0x3c, 0x3c, 0x3c, 0x3c, 0x1c, 0x38,
    0x1c, 0x38,

    /* U+58 "X" */
    0x0, 0xe, 0x38, 0xce, 0x1d, 0xc1, 0xf0, 0x3e,
    0x3, 0x80, 0xf0, 0x1f, 0x7, 0x70, 0xce, 0x38,
    0xee, 0x1c,

    /* U+59 "Y" */
    0x0, 0xe, 0x39, 0xce, 0x19, 0xc3, 0xb0, 0x3e,
    0x7, 0x80, 0x70, 0xe, 0x1, 0xc0, 0x38, 0x7,
    0x0, 0xe0,

    /* U+5A "Z" */
    0x0, 0x7f, 0xdf, 0xe0, 0xe0, 0xe0, 0x70, 0x70,
    0x38, 0x38, 0x1c, 0x1c, 0xf, 0xff, 0xf8,

    /* U+5B "[" */
    0x7, 0xfd, 0xce, 0x73, 0x9c, 0xe7, 0x39, 0xce,
    0x73, 0x9f, 0xf0,

    /* U+5C "\\" */
    0x0, 0x30, 0x18, 0x6, 0x3, 0x1, 0x80, 0x60,
    0x30, 0x18, 0x6, 0x3, 0x1, 0xc0, 0x60, 0x30,
    0xc, 0x6, 0x3, 0x0,

    /* U+5D "]" */
    0x7, 0xde, 0x73, 0x9c, 0xe7, 0x39, 0xce, 0x73,
    0x9c, 0xff, 0x78,

    /* U+5E "^" */
    0x0, 0xf, 0xf, 0x86, 0xe7, 0x38, 0x0,

    /* U+5F "_" */
    0xff, 0xbf, 0xe0, 0x0,

    /* U+60 "`" */
    0xe6, 0x30,

    /* U+61 "a" */
    0x0, 0x7e, 0x7f, 0x7, 0x7, 0x7f, 0x67, 0xe7,
    0x7f, 0x7f, 0x0,

    /* U+62 "b" */
    0x80, 0xc0, 0xc0, 0xc0, 0xfc, 0xfe, 0xe6, 0xc7,
    0xc7, 0xc7, 0xe6, 0xfe, 0xfc, 0x0,

    /* U+63 "c" */
    0x0, 0x3e, 0x7f, 0x60, 0x60, 0xe0, 0x60, 0x60,
    0x7f, 0x3e, 0x0,

    /* U+64 "d" */
    0x2, 0x1, 0xc0, 0xe0, 0x73, 0xfb, 0xfd, 0x8e,
    0xc7, 0xe3, 0xb1, 0xd8, 0xef, 0xf3, 0xf8, 0x0,

    /* U+65 "e" */
    0x0, 0x3c, 0x7e, 0x67, 0x67, 0xff, 0x60, 0x60,
    0x7f, 0x3e, 0x0,

    /* U+66 "f" */
    0x0, 0xe7, 0x9c, 0xfb, 0xe7, 0x1c, 0x71, 0xc7,
    0x1c, 0x70,

    /* U+67 "g" */
    0x0, 0x1f, 0xdf, 0xec, 0x76, 0x3f, 0x1d, 0x8e,
    0xc7, 0x7f, 0x9f, 0x80, 0xce, 0xe7, 0xe0, 0xc0,

    /* U+68 "h" */
    0x80, 0xc0, 0xc0, 0xc0, 0xfc, 0xfe, 0xe6, 0xc7,
    0xc7, 0xc7, 0xc7, 0xc7, 0xc7,

    /* U+69 "i" */
    0x9f, 0xf, 0xff, 0xff, 0xfe,

    /* U+6A "j" */
    0x47, 0x60, 0x77, 0x77, 0x77, 0x77, 0x77, 0xee,
    0x0,

    /* U+6B "k" */
    0x80, 0xc0, 0xc0, 0xc0, 0xce, 0xcc, 0xd8, 0xf8,
    0xf8, 0xfc, 0xdc, 0xce, 0xc7,

    /* U+6C "l" */
    0x8c, 0xcc, 0xcc, 0xcc, 0xcc, 0xcf, 0x70,

    /* U+6D "m" */
    0x0, 0x7, 0xef, 0x3f, 0xfd, 0xce, 0x6c, 0x63,
    0x63, 0x1f, 0x18, 0xf8, 0xc7, 0xc6, 0x3e, 0x31,
    0xc0,

    /* U+6E "n" */
    0x0, 0xfc, 0xfe, 0xe6, 0xc7, 0xc7, 0xc7, 0xc7,
    0xc7, 0xc7,

    /* U+6F "o" */
    0x0, 0x1f, 0x1f, 0xcc, 0x66, 0x37, 0x1d, 0x8c,
    0xc6, 0x7f, 0x1f, 0x0, 0x0,

    /* U+70 "p" */
    0x0, 0xfc, 0xfe, 0xe7, 0xc7, 0xc7, 0xc7, 0xe7,
    0xfe, 0xfc, 0xc0, 0xc0, 0xc0, 0xc0,

    /* U+71 "q" */
    0x0, 0x1f, 0xdf, 0xec, 0x76, 0x3f, 0x1d, 0x8e,
    0xc7, 0x7f, 0x9f, 0xc0, 0xe0, 0x70, 0x38, 0x18,

    /* U+72 "r" */
    0x1, 0xfb, 0xf7, 0xc, 0x18, 0x30, 0x60, 0xc1,
    0x80,

    /* U+73 "s" */
    0x0, 0x3e, 0x7e, 0x60, 0x78, 0x3e, 0xf, 0x7,
    0x7e, 0x3e, 0x0,

    /* U+74 "t" */
    0x71, 0xcf, 0xff, 0x71, 0xc7, 0x1c, 0x70, 0xf3,
    0xc0,

    /* U+75 "u" */
    0xc7, 0xc7, 0xc7, 0xc7, 0xc7, 0xc7, 0xe7, 0xff,
    0x7f, 0x0,

    /* U+76 "v" */
    0xe3, 0xb1, 0xd8, 0xce, 0xe3, 0x61, 0xf0, 0xf8,
    0x38, 0x1c, 0x0,

    /* U+77 "w" */
    0xe6, 0x3f, 0x39, 0x99, 0xcc, 0xdf, 0x67, 0xdf,
    0x1e, 0xf0, 0xe3, 0x87, 0x1c, 0x38, 0xc0,

    /* U+78 "x" */
    0x63, 0x3b, 0x8f, 0x87, 0x81, 0xc1, 0xe0, 0xf8,
    0xee, 0xe3, 0x0,

    /* U+79 "y" */
    0xe3, 0x31, 0x98, 0xce, 0xc3, 0x61, 0xf0, 0xf0,
    0x38, 0x1c, 0xc, 0x1e, 0xe, 0x0, 0x0,

    /* U+7A "z" */
    0xff, 0xfe, 0xe, 0x1c, 0x18, 0x38, 0x70, 0x7f,
    0xff,

    /* U+7B "{" */
    0x0, 0xf3, 0x8c, 0x30, 0xc3, 0xc, 0xf1, 0xc3,
    0xc, 0x30, 0xc3, 0xf, 0x18,

    /* U+7C "|" */
    0x4d, 0xb6, 0xdb, 0x6d, 0xb6, 0xdb, 0x60,

    /* U+7D "}" */
    0x3, 0xc7, 0xc, 0x30, 0xc3, 0xc, 0x3c, 0xe3,
    0xc, 0x30, 0xc3, 0x3c, 0x60,

    /* U+7E "~" */
    0x0, 0x1f, 0xe7, 0xf8, 0x0
};


/*---------------------
 *  GLYPH DESCRIPTION
 *--------------------*/

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {
    {.bitmap_index = 0, .adv_w = 0, .box_h = 0, .box_w = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */,
    {.bitmap_index = 0, .adv_w = 72, .box_h = 0, .box_w = 0, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 0, .adv_w = 72, .box_h = 13, .box_w = 3, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 5, .adv_w = 104, .box_h = 4, .box_w = 6, .ofs_x = 0, .ofs_y = 9},
    {.bitmap_index = 8, .adv_w = 177, .box_h = 13, .box_w = 11, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 26, .adv_w = 156, .box_h = 17, .box_w = 10, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 48, .adv_w = 219, .box_h = 14, .box_w = 14, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 73, .adv_w = 192, .box_h = 14, .box_w = 12, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 94, .adv_w = 58, .box_h = 4, .box_w = 3, .ofs_x = 0, .ofs_y = 9},
    {.bitmap_index = 96, .adv_w = 91, .box_h = 17, .box_w = 5, .ofs_x = 1, .ofs_y = -2},
    {.bitmap_index = 107, .adv_w = 91, .box_h = 17, .box_w = 5, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 118, .adv_w = 122, .box_h = 7, .box_w = 7, .ofs_x = 0, .ofs_y = 6},
    {.bitmap_index = 125, .adv_w = 156, .box_h = 8, .box_w = 7, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 132, .adv_w = 74, .box_h = 6, .box_w = 3, .ofs_x = 1, .ofs_y = -3},
    {.bitmap_index = 135, .adv_w = 92, .box_h = 3, .box_w = 6, .ofs_x = 0, .ofs_y = 4},
    {.bitmap_index = 138, .adv_w = 79, .box_h = 3, .box_w = 3, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 140, .adv_w = 140, .box_h = 17, .box_w = 8, .ofs_x = 1, .ofs_y = -2},
    {.bitmap_index = 157, .adv_w = 156, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 173, .adv_w = 156, .box_h = 13, .box_w = 5, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 182, .adv_w = 156, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 195, .adv_w = 156, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 211, .adv_w = 156, .box_h = 13, .box_w = 10, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 228, .adv_w = 156, .box_h = 14, .box_w = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 242, .adv_w = 156, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 258, .adv_w = 156, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 271, .adv_w = 156, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 287, .adv_w = 156, .box_h = 13, .box_w = 9, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 302, .adv_w = 71, .box_h = 9, .box_w = 3, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 306, .adv_w = 71, .box_h = 12, .box_w = 3, .ofs_x = 1, .ofs_y = -3},
    {.bitmap_index = 311, .adv_w = 156, .box_h = 9, .box_w = 7, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 319, .adv_w = 156, .box_h = 6, .box_w = 8, .ofs_x = 1, .ofs_y = 3},
    {.bitmap_index = 325, .adv_w = 156, .box_h = 9, .box_w = 6, .ofs_x = 2, .ofs_y = 2},
    {.bitmap_index = 332, .adv_w = 140, .box_h = 13, .box_w = 9, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 347, .adv_w = 259, .box_h = 16, .box_w = 16, .ofs_x = 0, .ofs_y = -3},
    {.bitmap_index = 379, .adv_w = 175, .box_h = 13, .box_w = 11, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 397, .adv_w = 175, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 414, .adv_w = 171, .box_h = 14, .box_w = 11, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 434, .adv_w = 180, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 451, .adv_w = 152, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 464, .adv_w = 150, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 477, .adv_w = 176, .box_h = 14, .box_w = 11, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 497, .adv_w = 189, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 514, .adv_w = 85, .box_h = 13, .box_w = 3, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 519, .adv_w = 147, .box_h = 14, .box_w = 8, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 533, .adv_w = 186, .box_h = 13, .box_w = 11, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 551, .adv_w = 145, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 564, .adv_w = 226, .box_h = 13, .box_w = 12, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 584, .adv_w = 189, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 601, .adv_w = 179, .box_h = 14, .box_w = 11, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 621, .adv_w = 170, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 638, .adv_w = 181, .box_h = 14, .box_w = 12, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 659, .adv_w = 178, .box_h = 13, .box_w = 10, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 676, .adv_w = 166, .box_h = 14, .box_w = 10, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 694, .adv_w = 154, .box_h = 13, .box_w = 10, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 711, .adv_w = 192, .box_h = 14, .box_w = 10, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 729, .adv_w = 177, .box_h = 13, .box_w = 11, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 747, .adv_w = 256, .box_h = 13, .box_w = 16, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 773, .adv_w = 170, .box_h = 13, .box_w = 11, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 791, .adv_w = 168, .box_h = 13, .box_w = 11, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 809, .adv_w = 149, .box_h = 13, .box_w = 9, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 824, .adv_w = 96, .box_h = 17, .box_w = 5, .ofs_x = 1, .ofs_y = -2},
    {.bitmap_index = 835, .adv_w = 140, .box_h = 17, .box_w = 9, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 855, .adv_w = 96, .box_h = 17, .box_w = 5, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 866, .adv_w = 156, .box_h = 6, .box_w = 9, .ofs_x = 0, .ofs_y = 7},
    {.bitmap_index = 873, .adv_w = 151, .box_h = 3, .box_w = 10, .ofs_x = 0, .ofs_y = -4},
    {.bitmap_index = 877, .adv_w = 97, .box_h = 3, .box_w = 4, .ofs_x = 1, .ofs_y = 10},
    {.bitmap_index = 879, .adv_w = 140, .box_h = 11, .box_w = 8, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 890, .adv_w = 147, .box_h = 14, .box_w = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 904, .adv_w = 128, .box_h = 11, .box_w = 8, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 915, .adv_w = 149, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 931, .adv_w = 140, .box_h = 11, .box_w = 8, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 942, .adv_w = 87, .box_h = 13, .box_w = 6, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 952, .adv_w = 149, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -4},
    {.bitmap_index = 968, .adv_w = 151, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 981, .adv_w = 75, .box_h = 13, .box_w = 3, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 986, .adv_w = 72, .box_h = 17, .box_w = 4, .ofs_x = 0, .ofs_y = -4},
    {.bitmap_index = 995, .adv_w = 145, .box_h = 13, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 1008, .adv_w = 82, .box_h = 13, .box_w = 4, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 1015, .adv_w = 229, .box_h = 10, .box_w = 13, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 1032, .adv_w = 151, .box_h = 10, .box_w = 8, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 1042, .adv_w = 144, .box_h = 11, .box_w = 9, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 1055, .adv_w = 149, .box_h = 14, .box_w = 8, .ofs_x = 1, .ofs_y = -4},
    {.bitmap_index = 1069, .adv_w = 149, .box_h = 14, .box_w = 9, .ofs_x = 0, .ofs_y = -4},
    {.bitmap_index = 1085, .adv_w = 118, .box_h = 10, .box_w = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 1094, .adv_w = 134, .box_h = 11, .box_w = 8, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 1105, .adv_w = 95, .box_h = 11, .box_w = 6, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1114, .adv_w = 151, .box_h = 10, .box_w = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 1124, .adv_w = 145, .box_h = 9, .box_w = 9, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1135, .adv_w = 206, .box_h = 9, .box_w = 13, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1150, .adv_w = 141, .box_h = 9, .box_w = 9, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1161, .adv_w = 138, .box_h = 13, .box_w = 9, .ofs_x = 0, .ofs_y = -4},
    {.bitmap_index = 1176, .adv_w = 129, .box_h = 9, .box_w = 8, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1185, .adv_w = 94, .box_h = 17, .box_w = 6, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 1198, .adv_w = 84, .box_h = 18, .box_w = 3, .ofs_x = 1, .ofs_y = -3},
    {.bitmap_index = 1205, .adv_w = 91, .box_h = 17, .box_w = 6, .ofs_x = 0, .ofs_y = -2},
    {.bitmap_index = 1218, .adv_w = 156, .box_h = 4, .box_w = 10, .ofs_x = 0, .ofs_y = 4}
};

/*---------------------
 *  CHARACTER MAPPING
 *--------------------*/



/*Collect the unicode lists and glyph_id offsets*/
static const lv_font_fmt_txt_cmap_t cmaps[] =
{
    {
        .range_start = 32, .range_length = 95, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY,
        .glyph_id_start = 1, .unicode_list = NULL, .glyph_id_ofs_list = NULL, .list_length = 0
    }
};

/*-----------------
 *    KERNING
 *----------------*/


/*Map glyph_ids to kern left classes*/
static const uint8_t kern_left_class_mapping[] =
{
    0, 0, 0, 1, 0, 0, 0, 0,
    1, 2, 0, 3, 0, 4, 5, 6,
    0, 0, 0, 0, 0, 0, 0, 0,
    7, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 8, 0, 9, 10, 0, 11,
    12, 0, 0, 13, 14, 15, 0, 0,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 2, 0, 0, 0,
    0, 0, 28, 29, 30, 0, 31, 32,
    33, 34, 0, 0, 35, 36, 37, 38,
    39, 39, 40, 41, 42, 43, 44, 45,
    46, 47, 48, 49, 2, 0, 0, 0
};

/*Map glyph_ids to kern right classes*/
static const uint8_t kern_right_class_mapping[] =
{
    0, 0, 0, 1, 0, 0, 0, 0,
    1, 0, 2, 3, 0, 4, 5, 4,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 6, 0, 7, 0, 0, 0,
    8, 0, 0, 9, 0, 0, 0, 0,
    8, 0, 8, 0, 10, 11, 12, 13,
    14, 15, 16, 17, 0, 0, 2, 0,
    0, 0, 18, 0, 19, 20, 19, 0,
    20, 0, 0, 21, 0, 0, 22, 22,
    20, 22, 20, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 0, 0, 2, 0
};

/*Kern values between classes*/
static const uint8_t kern_class_values[] =
{
    0, 0, 0, -9, -5, -11, -6, -6,
    -20, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -5, -5, 0, 0, 0, 0,
    0, 0, 0, -2, 0, -3, 0, 10,
    0, 0, -1, 6, 0, 0, 0, 0,
    4, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 2, 0, 0, 0, 0, 0, -14,
    0, -13, 0, 0, -25, 0, 0, 0,
    0, 0, -3, 0, 0, 0, -2, -2,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -9, 0, -14, 0, -7, 6,
    -6, -6, -1, 0, -15, 0, -14, -8,
    0, -14, 0, 0, -3, -3, 0, 0,
    0, -6, 0, -8, -5, 0, -8, 0,
    -5, -1, 0, -2, 0, -3, 0, 0,
    -11, 0, -9, 0, -5, -3, -6, -9,
    -4, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -3, 0, -1, -9, 0,
    -14, 0, -7, 0, -6, -6, -1, 0,
    -15, 0, -14, -8, 0, -14, 0, 0,
    -3, -3, 0, 0, 0, -6, 0, -8,
    -5, 0, -8, 0, 0, 0, 0, -18,
    -9, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -11, 6, -13, 0, -3, 6,
    -6, -6, 4, 0, -11, -1, -13, -3,
    2, -15, 0, 0, -1, -1, 0, 0,
    0, -3, 0, -7, -3, 4, -7, -1,
    -2, 0, 0, -3, 0, -2, -2, -2,
    -3, 0, -4, 0, -4, -2, -7, -5,
    -2, -3, 0, 0, 0, 0, 0, 0,
    0, -3, 0, -4, -3, -4, -6, 0,
    0, -6, 0, -6, 0, 0, -4, -2,
    -2, 0, -5, 0, -5, -8, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, -3, -2, 0, 0, 0, 0, -10,
    0, -7, 0, 0, -19, 0, 0, 0,
    -1, 0, -2, -1, -1, -5, -7, -7,
    0, 0, -2, 0, 0, -4, -3, -7,
    -4, -5, 0, 0, 0, 0, 0, -5,
    0, 0, -5, 0, -2, 0, -4, 0,
    -4, -7, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, -6, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -1, 0, 0, 0,
    0, 0, 0, -1, -1, 0, -3, 0,
    -6, 0, -9, 2, -9, -9, -4, -5,
    -4, -3, -5, -2, 0, -5, 0, -7,
    -9, -9, 0, 0, -3, -7, -5, -16,
    -10, 0, -16, -3, -16, 0, -16, 0,
    -6, 5, -7, -7, 5, 0, -15, 0,
    -20, -12, 0, -24, 0, 0, 0, 0,
    0, 0, 0, -3, 0, -16, -8, 0,
    -16, 0, -6, 0, 0, -6, 0, -6,
    0, 0, -6, -2, -2, 0, -5, 0,
    -5, -8, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, -3, -2, 0,
    0, 0, 0, -19, 0, -14, 0, 0,
    -30, 0, 0, 0, 0, 0, -10, -4,
    -1, -5, -6, -6, -1, 0, 0, 0,
    0, 0, 1, -2, 0, -3, -6, 0,
    0, -6, 0, 4, 0, 0, 3, -2,
    -2, 0, -5, 0, -3, -8, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, -3, -2, 0, 0, 0, 0, -2,
    -1, 2, -1, -1, -1, 0, -3, 0,
    -5, -1, 0, -8, -1, -2, -4, -4,
    0, 0, 0, 0, 0, -3, 0, 0,
    -3, 0, 0, 0, 0, 0, 0, -3,
    0, 0, -1, 0, -1, 0, -1, 0,
    -5, -2, 0, 0, 0, 0, -1, 0,
    0, 0, 0, -7, -5, -5, -7, 0,
    0, 0, 0, -15, -9, -11, -2, -2,
    -23, 0, 1, 0, 0, 0, -4, 0,
    0, -12, -17, -17, -1, -6, -8, -5,
    -6, -15, -13, -16, -15, -9, 0, 0,
    0, 0, 0, -1, 0, 0, -7, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -2, 0, 0, 0,
    0, -2, -1, 0, 0, 2, 0, -14,
    -5, -13, -5, -5, -21, -3, 0, 0,
    4, 4, -1, 4, 0, -8, -13, -13,
    0, -2, -5, -1, -2, -3, 0, -7,
    -3, -6, 0, 2, 0, -8, -3, -3,
    0, 0, -12, 0, 0, 0, 4, 2,
    0, 4, 0, -4, -6, -6, 0, 0,
    0, 0, 0, 0, 0, -4, 0, -2,
    0, 2, -3, 0, -6, 2, -5, -5,
    0, 0, -4, 0, -1, 0, 0, -2,
    0, -3, -7, -7, 0, 0, -1, -4,
    0, -9, -5, 0, -9, -1, 0, 2,
    0, -14, -9, -15, -6, -6, -26, -5,
    0, 0, 4, 4, -2, 4, 0, -14,
    -20, -20, 0, -8, -16, -3, -8, -9,
    -8, -12, -9, -11, 0, 0, 0, 0,
    -6, 0, -1, -1, 2, 0, 0, 0,
    0, 0, 0, 0, 0, -1, -1, -1,
    0, 0, 0, 0, 0, -4, -2, 0,
    -4, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -12, 0, -10, -5,
    0, -16, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -3, -3, 0, -4, 0,
    -5, 0, -2, -3, 0, -1, 0, 0,
    0, 0, -17, 0, -13, -5, -5, -20,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, -4, -2, -7, -4, 0, -3, 0,
    0, -2, -3, 0, 0, 0, 2, 0,
    -16, 0, -8, -4, 0, -14, 0, -1,
    -2, -2, 0, 0, 0, 0, 0, 0,
    0, -2, 0, 0, -7, 0, -4, -2,
    0, 0, 0, 0, 0, 0, -17, 0,
    -14, -5, 0, -19, 0, 0, 0, 0,
    0, 0, 0, 0, 0, -5, -2, -7,
    -5, 0, 0, 0, 0, -5, -1, -1,
    0, 0, -5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -4, 0, -3, 0, 0, -10,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, -5, 0,
    -1, 0, 0, 0, 0, 0, 0, 0,
    -16, 0, -14, -5, 0, -17, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -4, 0, 0, 0, 0, 0,
    0, 4, -1, -2, 0, 0, -12, -2,
    -10, -6, 0, -14, 0, 0, -2, -10,
    0, 0, 0, 0, 0, 0, 0, 0,
    -2, 0, 0, 0, 0, 0, 0, 3,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -15, 0, -14, -5, 0, -16,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    -15, 0, -14, -5, 0, -16, 0, 0,
    0, 0, 0, 0, 0, 0, 0, -3,
    0, 0, -4, 0, -5, 0, -2, -3,
    0, -1, 0, 0, 0, 0, -17, 0,
    -13, -6, -5, -20, 0, 0, 0, 0,
    0, 0, 0, 0, 0, -4, -2, -7,
    -4, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -4, 0, -2, 0,
    0, -9, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -14, 0, -10, 0, 0,
    -29, 0, -17, 0, -6, -2, 0, -14,
    0, -2, -2, -2, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, -1, 0,
    -20, 0, -15, -9, 0, -19, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, -2, 0, -2, 0, 0, 0,
    0, 0, 0, 0, 1, 0, -7, 0,
    -3, 0, 0, -5, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, -7, 0, -2, 0,
    0, -9, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -8, 0, -7, 0, 0,
    -17, 0, -16, 0, 0, 0, -9, -9,
    0, -1, -4, -4, 0, 0, 0, 2,
    0, 3, 3, 0, 3, -2, 0, 0,
    0, -5, 0, -3, 0, 0, -12, 0,
    -15, 0, 0, 0, -5, -8, 0, 0,
    -2, -2, 0, 0, 0, 0, 0, 2,
    2, 0, 2, 0, 0, 0, 0, 0,
    -3, 0, -4, -4, 0, 0, -16, -3,
    -6, -3, 0, -12, 0, -2, -7, -7,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, -8, 0, -7,
    0, 0, -17, 0, -16, 0, -1, 0,
    -9, -9, 0, -1, -4, -4, 0, 0,
    0, 2, 0, 3, 3, 0, 3, -2,
    -3, 0, 0, 0, -1, 0, 0, 0,
    0, 0, -12, 0, -7, -1, 0, -11,
    0, -1, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0
};


/*Collect the kern class' data in one place*/
static const lv_font_fmt_txt_kern_classes_t kern_classes =
{
    .class_pair_values   = kern_class_values,
    .left_class_mapping  = kern_left_class_mapping,
    .right_class_mapping = kern_right_class_mapping,
    .left_class_cnt      = 49,
    .right_class_cnt     = 30,
};

/*--------------------
 *  ALL CUSTOM DATA
 *--------------------*/

/*Store all the custom data of the font*/
static lv_font_fmt_txt_dsc_t font_dsc = {
    .glyph_bitmap = gylph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .cmap_num = 1,
    .bpp = 1,

    .kern_scale = 16,
    .kern_dsc = &kern_classes,
    .kern_classes = 1
};


/*-----------------
 *  PUBLIC FONT
 *----------------*/

/*Initialize a public general font descriptor*/
lv_font_t din2014_18 = {
    .dsc = &font_dsc,          /*The custom font data. Will be accessed by `get_glyph_bitmap/dsc` */
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,    /*Function pointer to get glyph's bitmap*/
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,    /*Function pointer to get glyph's data*/
    .line_height = 19,          /*The maximum line height required by the font*/
    .base_line = 4,             /*Baseline measured from the bottom of the line*/
};

#endif /*#if DIN2014_18*/

