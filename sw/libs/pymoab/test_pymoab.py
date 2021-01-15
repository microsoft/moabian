# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pymoab import *
from time import sleep

def test_display():
    init()

    # display all the icons
    print("cycling icons")
    sleep(1)
    icons = list(Icon)
    for icon in icons:
        setIcon(icon)
        sync()
        sleep(0.1)

    # display all the text
    print("cycling text")
    sleep(1)
    texts = list(Text)
    for text in texts:
        setText(text)
        sync()
        sleep(0.1)

    # display all the text
    print("plate angles")
    setIcon(Icon.BLANK)
    setText(Text.MANUAL)
    sync()
    sleep(1)
    lowerPlate()
    sync()
    sleep(1)
    activatePlate()
    sync()
    sleep(1)

    angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

    for angle in angles:
        sleep(0.5)
        setPlateAngles(angle[0], angle[1])
        sync()

    print("press joystick")
    sleep(1)
    while not getJoystickBtn():
        sleep(0.01)
        sync()

    print("press menu")
    sleep(1)
    while not getMenuBtn():
        sleep(0.01)
        sync()

    print("joy right")
    sleep(1)
    while getJoystickX() < 0.5:
        sleep(0.01)
        sync()

    print("joy left")
    sleep(1)
    while getJoystickX() > -0.5:
        sleep(0.01)
        sync()

    print("joy up")
    sleep(1)
    while getJoystickY() < 0.5:
        sleep(0.01)
        sync()

    print("joy down")
    sleep(1)
    while getJoystickY() > -0.5:
        sleep(0.01)
        sync()


if __name__ == "__main__":
    test_display()
