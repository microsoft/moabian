# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from hat import Hat
from time import sleep


def test_display():
    # display all the icons
    # print("cycling icons")
    # sleep(1)
    # icons = list(Icon)
    # for icon in icons:
    #     set_icon_text(icon, Text.MANUAL)
    #     sleep(0.1)

    # # display all the text
    # print("cycling text")
    # sleep(1)
    # texts = list(Text)
    # for text in texts:
    #     set_icon_text(Icon.BLANK, text)
    #     sleep(0.1)

    # display all the text
    with Hat() as hat:
        hat.enable_servos()
        sleep(0.5)

        angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

        for angle in angles:
            hat.set_angles(angle[0], angle[1])
            sleep(0.5)

if __name__ == "__main__":
    test_display()
