# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from interface import *
from time import sleep


def test_display():
    init()

    # display all the icons
    print("cycling icons")
    sleep(1)
    icons = list(Icon)
    for icon in icons:
        set_icon_text(icon, Text.MANUAL)
        sync()
        sleep(0.1)

    # display all the text
    print("cycling text")
    sleep(1)
    texts = list(Text)
    for text in texts:
        set_icon_text(Icon.BLANK, text)
        sync()
        sleep(0.1)

    # display all the text
    print("plate angles")
    set_icon_text(Icon.BLANK, Text.MANUAL)
    sync()
    sleep(1)
    lower_plate()
    sync()
    sleep(1)
    activate_plate()
    sync()
    sleep(1)

    angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

    for angle in angles:
        sleep(0.5)
        set_plate_angles(angle[0], angle[1])
        sync()

    print("press joystick")
    sleep(1)
    while not get_joystick_btn():
        sleep(0.01)
        sync()

    print("press menu")
    sleep(1)
    while not get_menu_btn():
        sleep(0.01)
        sync()

    print("joy right")
    sleep(1)
    while get_joystick_x() < 0.5:
        sleep(0.01)
        sync()

    print("joy left")
    sleep(1)
    while get_joystick_x() > -0.5:
        sleep(0.01)
        sync()

    print("joy up")
    sleep(1)
    while get_joystick_y() < 0.5:
        sleep(0.01)
        sync()

    print("joy down")
    sleep(1)
    while get_joystick_y() > -0.5:
        sleep(0.01)
        sync()


if __name__ == "__main__":
    test_display()

