#!/usr/bin/env python3

import time
import numpy as np
from typing import Union, List, Tuple, Dict

class color:
    green = '\033[38;5;112m'
    cyan = '\033[38;5;165m'
    red = '\033[31m'
    yellow = '\033[33m'
    gray = '\033[38;5;242m'
    end = '\033[0m'

# TODO: use pythonic map/reduce itertools

def hexyl():
    tick = 0

    def wrap(c : Union[str, None], s):
        # first byte like 31 to string 0x1F
        byte = f'{np.uint8(s):02x}'
        if c is None:
            return byte
        else:
            return c + byte + color.end

    def enumerate_bytes(bytelist, c : Dict):
        for i, v in enumerate(bytelist):
            yield wrap(c.get(i), v)

    def tx_list(l):
        c = {0: color.red, 4: color.yellow}
        return ' '.join(enumerate_bytes(l, c))

    def rx_list(l):
        c = {0: color.green, 1: color.cyan, 2: color.cyan}
        return ' '.join(enumerate_bytes(l, c))

    def hfn(tx, rx):
        nonlocal tick
        tick = tick + 1

        print(f'{color.gray}{tick:05d}{color.end}', end='')
        print(" ┊ ", end='')

        print(tx_list(tx), end='')
        print(" ┊ ", end='')

        print(rx_list(rx), end='')
        print('')

    return hfn


def main():
    tx = np.random.randint(255, size=8)
    rx = np.random.randint(255, size=8)

    t = hexyl()
    t(tx, rx)

    tx = np.random.randint(255, size=8)
    rx = np.random.randint(255, size=8)
    t(tx, rx)

if __name__ == "__main__":
    main()
