#!/usr/bin/env python3

import time
import numpy as np
import itertools
from operator import add
from typing import Union, List, Tuple, Dict


class color:
    green = "\033[38;5;40m"
    cyan = "\033[38;5;111m"
    red = "\033[31m"
    yellow = "\033[38;5;40m"
    string = "\033[38;5;40m"
    string_cmd = "\033[38;5;34m"
    gray = "\033[38;5;242m"
    darkgray = "\033[38;5;238m"
    danger = "\033[38;5;196m"
    servos = "\033[38;5;19m"
    end = "\033[0m"


# TODO: use pythonic map/reduce itertools


def hexyl():
    tick = 0

    def wrapstr(c: Union[str, None], s):
        if c is None:
            return s
        else:
            return c + s + color.end

    def wrap_tx(c: Union[str, None], s):
        # first byte like 31 to string 0x1F
        byte = f"{np.uint8(s):02x}"
        if byte == "00":
            c = color.darkgray
        if c is None:
            return byte
        else:
            return c + byte + color.end

    def enum_bytes_tx(bytelist, c: Dict):
        for i, v in enumerate(bytelist):
            yield wrap_tx(c.get(i), v)

    def wrap_rx(clr: Union[str, None], the_byte, position):
        # first byte like 31 to string 0x1F
        byte_str = f"{np.uint8(the_byte):02x}"

        # first two bytes are buttons
        # second two bytes are joystick
        # last four bytes should always be zero

        # unused bytes
        if position > 3:
            if byte_str == "00":  # nominal
                clr = color.darkgray
            else:
                clr = color.danger

        if position <= 1:
            if byte_str == "00":  # nominal
                clr = color.darkgray

        if clr is None:
            clr = color.darkgray

        return clr + byte_str + color.end

    def enum_bytes_rx(bytelist, c: Dict):
        for i, v in enumerate(bytelist):
            yield wrap_rx(c.get(i), v, i)

    def tx_list(l):
        if np.uint8(l[0]) == 0x80:
            c = {0: color.green}
            c.update({k: color.yellow for k in range(1, 9)})
        else:
            c = {0: color.red}

        return " ".join(enum_bytes_tx(l, c))

    def printable(c):
        if c > 0x1F & c < 0x7F:
            return chr(c)
        if c == 0x0A:
            return "¶"
        else:
            return "·"

    def tx_to_english(l):
        b1 = np.uint8(l[0])
        if b1 == 0x80:
            remainder = l[1:]
            return " ┊ " + color.string + "".join(map(printable, remainder)) + color.end
        elif b1 == 0x01:
            return " ┊ " + wrapstr(color.red, "servos: on")
        elif b1 == 0x02:
            return " ┊ " + wrapstr(color.red, "servos: off")
        elif b1 == 0x05:
            s1 = ((l[1] << 8) + l[2]) / 100
            s2 = ((l[3] << 8) + l[4]) / 100
            s3 = ((l[5] << 8) + l[6]) / 100

            s = f"{s1:6.2f}, {s2:6.2f}, {s3:6.2f}"
            return " ┊ " + wrapstr(color.servos, s)
        elif b1 == 0x06:
            return " ┊ " + wrapstr(color.green, "text/icon")
        elif b1 >= 0x81 and b1 <= 0x85:
            return " ┊ " + wrapstr(color.string_cmd, "◊")
        else:
            return ""

    def rx_list(l):
        c = {0: color.green, 1: color.green, 2: color.cyan, 3: color.cyan}
        return " ".join(enum_bytes_rx(l, c))

    def canary(l):
        if (
            np.uint8(l[0]) > 0x01
            or np.uint(l[1]) > 0x01
            or sum(np.uint(l[4:8])) > 0
            or abs(np.int8(l[2])) > 100
            or abs(np.int8(l[3]) > 100)
        ):
            return wrapstr(color.red, " FATAL")
        else:
            return ""

    # verbosity spi debug
    # 0: nothing
    # 1: mode changes
    # 2: include servo settings (0x05)
    # 3: include noops (0x00) (useful to show menu/joystick state)

    def hfn(tx, rx, verbose=0):
        nonlocal tick
        tick = tick + 1

        if verbose == 0:
            return

        if np.uint8(tx[0]) == 0x05 and verbose < 2:
            return

        if np.uint8(tx[0]) == 0x00 and verbose < 3:
            return

        # Print a 5-digit tick that updates every 30 Hz
        print(f"{color.gray}{tick:05d}{color.end}", end="")
        print(" ┊ ", end="")

        # Tx 8 bytes: transmit to Hat
        print(tx_list(tx), end="")
        print(" ┊ ", end="")

        # Rx 8 bytes: receive bytes back from Hat
        print(rx_list(rx), end="")

        # Translate some of the bytes
        print(tx_to_english(tx), end="")

        # Scan for unusual bytes
        print(canary(rx))

    return hfn


def main():
    tx1 = [0x05, 0x32, 0x5F, 0x2C, 0x64, 0x35, 0x62, 0x00]

    rx0 = [0x00, 0x00, 0x5F, 0x2C, 0x00, 0x00, 0x00, 0x00]  # good
    rx1 = [0x01, 0x01, 0x3F, 0x2C, 0x00, 0x00, 0x00, 0x00]  # rest are bad
    rx2 = [0x05, 0x00, 0x3F, 0x2C, 0x01, 0x01, 0x00, 0x00]  # badd 4-byte range
    rx3 = [0x05, 0x00, 0x3F, 0x2C, 0x00, 0x00, 0x00, 0x00]  # bad button down
    rx4 = [0x00, 0x00, 0x3F, 0x2C, 0x00, 0x99, 0x00, 0x00]  # bad 4-byte
    rx5 = [0x00, 0x00, 0x6F, 0x5C, 0x00, 0x00, 0x00, 0x00]  # bad joy stick (x)
    rx6 = [0x00, 0x00, 0x5F, 0x6F, 0x00, 0x00, 0x00, 0x00]  # bad joy stick (y)

    t = hexyl()
    t(tx1, rx0, verbose=4)
    t(tx1, rx1, verbose=4)
    t(tx1, rx2, verbose=4)
    t(tx1, rx3, verbose=4)
    t(tx1, rx4, verbose=4)
    t(tx1, rx5, verbose=4)
    t(tx1, rx6, verbose=4)


if __name__ == "__main__":
    main()
