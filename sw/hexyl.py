#!/usr/bin/env python3

import time
import numpy as np
import itertools
from operator import add
from typing import Union, List, Tuple, Dict

class color:
    green = '\033[38;5;112m'
    cyan = '\033[38;5;165m'
    red = '\033[31m'
    yellow = '\033[33m'
    gray = '\033[38;5;242m'
    darkgray = '\033[38;5;238m'
    end = '\033[0m'

# TODO: use pythonic map/reduce itertools

def hexyl():
    tick = 0

    def wrapstr(c : Union[str, None], s):
        if c is None:
            return s
        else:
            return c + s + color.end

    def wrap(c : Union[str, None], s):
        # first byte like 31 to string 0x1F
        byte = f'{np.uint8(s):02x}'
        if byte == '00':
            c = color.darkgray
        if c is None:
            return byte
        else:
            return c + byte + color.end

    def enumerate_bytes(bytelist, c : Dict):
        for i, v in enumerate(bytelist):
            yield wrap(c.get(i), v)

    def tx_list(l):
        if np.uint8(l[0]) == 0x80:
            c = {0: color.green}
            c.update({k: color.yellow for k in range(1,9)})
        else:
            c = {0: color.red}

        return ' '.join(enumerate_bytes(l, c))

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
        elif b1 == 0x06:
           return(" ┊ " + wrapstr(color.green, 'text/icon'))
        elif b1 == 0x81:
           return(" ┊ " + wrapstr(color.red, 'display buffer'))
        else:
            return('')

    def rx_list(l):
        c = {0: color.green, 1: color.cyan, 2: color.cyan}
        return ' '.join(enumerate_bytes(l, c))

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
    tx1 = [0x80,  0x4c, 0x6f, 0x61, 0x64,  0x2d, 0x62, 0x65, 0x61]
    tx2 = [0x80,  0x72, 0x69, 0x6e, 0x67,  0x0a, 0x50, 0x6f, 0x73]
    tx3 = [0x80,  0x74, 0x65, 0x72, 0x00,  0x00, 0x00, 0x00, 0x00]

    t = hexyl()
    t(tx1, np.random.randint(255, size=9))
    t(tx2, np.random.randint(255, size=9))
    t(tx3, np.random.randint(255, size=9))

    tx = np.random.randint(255, size=9)
    rx = np.random.randint(255, size=9)
    t(tx, rx)

    tx = np.random.randint(255, size=9)
    rx = np.random.randint(255, size=9)
    t(tx, rx)

if __name__ == "__main__":
    main()
