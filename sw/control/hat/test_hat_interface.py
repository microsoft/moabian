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
                sleep(0.1)

    # display all the text
    print("cycling text")
    sleep(1)
    texts = list(Text)
    for text in texts:
        set_icon_text(Icon.BLANK, text)
                sleep(0.1)

    # display all the text
    print("plate angles")
    set_icon_text(Icon.BLANK, Text.MANUAL)
        sleep(1)
    lower_plate()
        sleep(1)
    activate_plate()
        sleep(1)

    angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

    for angle in angles:
        sleep(0.5)
        set_plate_angles(angle[0], angle[1])
        
    print("press joystick")
    sleep(1)
    while not get_joystick_btn():
        sleep(0.01)
        
    print("press menu")
    sleep(1)
    while not get_menu_btn():
        sleep(0.01)
        
    print("joy right")
    sleep(1)
    while get_joystick_x() < 0.5:
        sleep(0.01)
        
    print("joy left")
    sleep(1)
    while get_joystick_x() > -0.5:
        sleep(0.01)
        
    print("joy up")
    sleep(1)
    while get_joystick_y() < 0.5:
        sleep(0.01)
        
    print("joy down")
    sleep(1)
    while get_joystick_y() > -0.5:
        sleep(0.01)
        

if __name__ == "__main__":
    test_display()

