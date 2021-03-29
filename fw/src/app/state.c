// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "state.h"

atomic_t g_joy_x = ATOMIC_INIT(0);
atomic_t g_joy_y = ATOMIC_INIT(0);
atomic_t g_btn_joy = ATOMIC_INIT(0);
atomic_t g_btn_menu = ATOMIC_INIT(0);
