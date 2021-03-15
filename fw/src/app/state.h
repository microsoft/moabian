#ifndef STATUS_H
#define STATUS_H

// 32-bit integers are the only atomic types
extern atomic_t g_joy_x;
extern atomic_t g_joy_y;
extern atomic_t g_btn_menu;
extern atomic_t g_btn_joy;

#endif
