#!/usr/bin/env python3

import time
import numpy as np
import itertools
from operator import add
from typing import Union, List, Tuple, Dict

class color:
    green = '\033[38;5;40m'
    cyan = '\033[38;5;111m'
    red = '\033[31m'
    yellow = '\033[33m'
    gray = '\033[38;5;242m'
    darkgray = '\033[38;5;238m'
    danger = '\033[38;5;196m'
    end = '\033[0m'

# TODO: use pythonic map/reduce itertools

def hexyl():
    tick = 0

    def wrapstr(c : Union[str, None], s):
        if c is None:
            return s
        else:
            return c + s + color.end

    def wrap_tx(c : Union[str, None], s):
        # first byte like 31 to string 0x1F
        byte = f'{np.uint8(s):02x}'
        if byte == '00':
            c = color.darkgray
        if c is None:
            return byte
        else:
            return c + byte + color.end

    def enum_bytes_tx(bytelist, c : Dict):
        for i, v in enumerate(bytelist):
            yield wrap_tx(c.get(i), v)

    def wrap_rx(clr : Union[str, None], the_byte, position):
        # first byte like 31 to string 0x1F
        byte_str = f'{np.uint8(the_byte):02x}'

        # first two bytes are buttons
        # second two bytes are joystick
        # last four bytes should always be zero

        # unused bytes
        if position > 3:
            if byte_str == '00':        # nominal
                clr = color.darkgray
            else:
                clr = color.danger

        if position <= 1:
            if byte_str == '00':        # nominal
                clr = color.darkgray

        if clr is None:
            clr = color.darkgray

        return clr + byte_str + color.end


    def enum_bytes_rx(bytelist, c : Dict):
        for i, v in enumerate(bytelist):
            yield wrap_rx(c.get(i), v, i)

    def tx_list(l):
        if np.uint8(l[0]) == 0x80:
            c = {0: color.green}
            c.update({k: color.yellow for k in range(1,9)})
        else:
            c = {0: color.red}

        return ' '.join(enum_bytes_tx(l, c))

    def printable(c):
        if c > 0x1F & c < 0x7F:
            return chr(c)
        if c == 0x0A:
            return '¶'
        else:
            return '·'

    def tx_80(l):
        b1 = np.uint8(l[0]);
        if b1 == 0x80:
            remainder = l[1:]
            return(" ┊ " + color.yellow + ''.join(map(printable, remainder)) + color.end)
        elif b1 == 0x01:
           return(" ┊ " + wrapstr(color.red, 'servo: enable'))
        elif b1 == 0x02:
           return(" ┊ " + wrapstr(color.red, 'servo: disable'))
        elif b1 == 0x03:
           return(" ┊ " + wrapstr(color.green, 'control info'))
        elif b1 == 0x04:
           return(" ┊ " + wrapstr(color.red, 'servo: plate angles'))
        elif b1 == 0x05:
           s1 = ((l[1] << 8) + l[2]) / 100
           s2 = ((l[3] << 8) + l[4]) / 100
           s3 = ((l[5] << 8) + l[6]) / 100

           s = f'{s1:6.2f}, {s2:6.2f}, {s3:6.2f}'
           return(" ┊ " + wrapstr(color.green, s))
        elif b1 == 0x06:
           return(" ┊ " + wrapstr(color.green, 'text/icon'))
        elif b1 == 0x81:
           return(" ┊ " + wrapstr(color.red, 'display buffer'))
        else:
            return('')

    def rx_list(l):
        c = {0: color.green, 1: color.green, 2: color.cyan, 3: color.cyan}
        return ' '.join(enum_bytes_rx(l, c))

    def hfn(tx, rx):
        nonlocal tick
        tick = tick + 1

        # if np.uint8(tx[0]) == 0x00:
        #     return

        print(f'{color.gray}{tick:05d}{color.end}', end='')
        print(" ┊ ", end='')

        print(tx_list(tx), end='')
        print(" ┊ ", end='')

        print(rx_list(rx), end='')

        print(tx_80(tx))

    return hfn


def main():
    tx1 = [0x05, 0x32, 0x6f, 0x2c, 0x64,  0x35, 0x62, 0x00]

    t = hexyl()
    t(tx1, np.random.randint(255, size=8))

if __name__ == "__main__":
    main()
