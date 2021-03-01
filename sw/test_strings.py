#!/usr/bin/env python3

import argparse

import time
from hat import Hat, Icon, Text, plate_angles_to_servo_positions

menus = {
    0: "Berkeley\nCalifornia",
    1: "Sacramento\nVacaville\nBerkeley\nSan Luis Obispo CA",
    2: "Sacramento Vacaville\nKansas City\nBerkeley San Luis Obispo CA",
}

def main(menu=0, frequency=30, debug=True):
    idx = menu

    with Hat() as hat:
        hat.print_arbitrary_string(menus[idx])

        while True:
            hat.noop()
            menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
            time.sleep(1 / frequency)

            if menu_btn:
                break;

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--menu",
        default="0",
        type=int,
        choices=list(menus.keys()),
        help=f"""Select what type of action to take.
        """,
    )
    parser.add_argument("-f", "--frequency", default="30", type=int)
    args, _ = parser.parse_known_args()
    main(args.menu, args.frequency)
