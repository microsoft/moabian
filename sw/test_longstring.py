#!/usr/bin/env python3

import time
from hat import Hat, Icon, Text, plate_angles_to_servo_positions

def main(frequency=30, debug=True):
    with Hat() as hat:
        # works
        hat.print_arbitrary_string("Step 1\nCalibrate Hue")
        #hat.print_arbitrary_string("aaa AAA\nBBB\n12 ccc CCC\n12 ddd DDD")
        #hat.set_icon_text(Icon.X, Text.CAL_INSTR)

        while True:
            hat.noop()
            menu_btn, joy_btn, joy_x, joy_y = hat.poll_buttons()
            time.sleep(1 / 30)
            if joy_btn:
                break


if __name__ == "__main__":
    main()
