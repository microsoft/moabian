import time
import sys

import parent
from hardware import MoabHardware
import procid


def main():

    procid.stop_doppelgänger()
    with MoabHardware(debug=True, verbose=2) as hw:
        hw.enable_servos()

        print(hw)
        # hw.servo_offsets = list(map(int, [-4, 0, -4]))

        for i in range(150, 130, -2):
            hw.set_servos(i, i, i)
            hw.display(f"Level {i}º")
            time.sleep(0.05)

        # set_angles sets the 3 servo positions (offset included)
        # pitch = 0, roll = 0

        angles = [(0, 0), (0, 15), (0, -15), (0, 0), (15, 0), (-15, 0), (0, 0)]

        for angle in angles:
            hw.set_angles(angle[0], angle[1])
            hw.display(f"P {angle[0]}, R: {angle[1]}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
