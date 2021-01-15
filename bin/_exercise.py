#!runpy.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pymoab import *
from time import sleep

# This needs to be called before INIT
# Also: do not call sync() on this (segfault)
print("setting servo offset")
set_servo_offsets(-2, 1, 0)

print("init()")
init()
sleep(0.1)

print("setting text and icon")
set_icon_text(Icon.DOT, Text.INIT)
sleep(0.1)


print("activating plate")
activate_plate()
sleep(0.1)

## ^ swap v these two lines and I bet bad things happen
## due to moab.c:90 and moab.c:91


print("cycling angles")
set_icon_text(Icon.PAUSE, Text.INFO)
sleep(0.2)
angles = [(0, 0), (0, 15), (15, 0), (0, -15), (-15, 0), (0, 0)]
for angle in angles:
    set_plate_angles(angle[0], angle[1])
        sleep(0.3)

print("menu -> Success")
set_icon_text(Icon.DOT, Text.CAL_COMPLETE)
sleep(0.2)

print("deactivating...")
lower_plate()
sleep(0.2)

# Due to firmware 2.1 bug, disable_servo_power sets icon=0 and text=0
print("cutting servo power...")
disable_servo_power()
sleep(0.2)

print("Menu -> Success (check)")
set_icon_text(Icon.CHECK, Text.CAL_COMPLETE)
sleep(0.2)
