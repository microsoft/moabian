#!/usr/bin/env python3

import argparse

import time
from hat import Hat, Icon, Text, plate_angles_to_servo_positions

menus = {
    0: "aa2 AAA\nBBB 123\n12 cc CCC\n12 ddd DDD",
    1: "aa2 AAA\nBBB 123\n12 ccc CCC\n12 ddd DDD",
    2: "aa23 AAA\nBBB 123\n12 ccc CCC\n12 ddd DDD",
    3: "aaa23 AAA\nBBB 123\n12 ccc CCC\n12 ddd DDD",
    4: "Step 1\nCalibrate Hue",
    5: "Hello Denise and Brooklyn\nbreak\me please",
}

def main(menu=0, frequency=10, debug=True):
    idx = menu

    with Hat() as hat:
        hat.print_arbitrary_string(menus[idx])

        while True:
            hat.noop()
            menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
            time.sleep(1 / frequency)
            if menu_btn:
                idx += 1
                hat.print_arbitrary_string(menus[idx % len(menus)])

            if joy_btn:
                break


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
    parser.add_argument("-f", "--frequency", default="5", type=int)
    parser.add_argument("-d", "--debug", action="store_true")
    args, _ = parser.parse_known_args()
    main(args.menu, args.frequency, args.debug)
