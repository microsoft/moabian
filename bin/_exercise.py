#!runpy.sh

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pymoab import *
from time import sleep

# This needs to be called before INIT
# Also: do not call sync() on this (segfault)
print("setting servo offset")
setServoOffsets(-2, 1, 0)

print("init()")
init()
sync()
sleep(0.1)

print("setting text and icon")
setText(Text.INIT)
setIcon(Icon.DOT)
sync()
sleep(0.1)


print("activating plate")
activatePlate()
sync()
sleep(0.1)

## ^ swap v these two lines and I bet bad things happen
## due to moab.c:90 and moab.c:91


print("cycling angles")
setText(Text.INFO)
setIcon(Icon.PAUSE)
sync()
sleep(0.2)
angles = [(0, 0), (0, 15), (15, 0), (0, -15), (-15, 0), (0, 0)]
for angle in angles:
    setPlateAngles(angle[0], angle[1])
    sync()
    sleep(0.3)

print("menu -> Success")
setText(Text.CAL_COMPLETE)
setIcon(Icon.DOT)
sync()
sleep(0.2)

print("deactivating...")
lowerPlate()
sync()
sleep(0.2)

# Due to firmware 2.1 bug, disableServoPower sets icon=0 and text=0
print("cutting servo power...")
disableServoPower()
sync()
sleep(0.2)

print("Menu -> Success (check)")
setText(Text.CAL_COMPLETE)
setIcon(Icon.CHECK)
sync()
sleep(0.2)
