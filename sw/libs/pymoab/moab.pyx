# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import math
import cython
import socket
from enum import IntEnum
from typing import Tuple

ctypedef char bool
ctypedef signed char int8_t
ctypedef unsigned char uint8_t



cdef float _bandpass_lookup[256]
cdef float _last_sigma = 0.0
cdef float _last_gain = 0.0
cdef unsigned char _last_center = 0

@cython.boundscheck(False)
@cython.wraparound(False)
def _update_bandpass_lookup(unsigned char center, float sigma, float gain):
    global _bandpass_lookup
    global _last_center
    global _last_gain
    global _last_sigma

    _last_center = center
    _last_sigma = sigma
    _last_gain = gain

    mu = 0.5
    for n in range(256):
        h = n / 255.0

        # rotate the hue phase so that `center` is at 0.5
        h = h + (0.5 - (center / 255.0))
        if (h > 1.0):
            h = h - 1.0
        if (h < 0.0):
            h = h + 1.0

        # gaussian bandpass filter
        f = math.exp(-( (h - mu)**2 / ( 2.0 * sigma**2 ) ) )

        # pre-gain around center
        f = f * gain
        if f > 1.0:
            f = 1.0

        _bandpass_lookup[n] = f


@cython.boundscheck(False)
@cython.wraparound(False)
def hue_mask(unsigned char [:, :, :] image, unsigned char center, float sigma, float gain, float mask_gain):
    global _bandpass_lookup

    # set the variable extension types
    cdef int x, y, n, width, height
    cdef float h, s, v, mu, f
    cdef unsigned char mask, ih

    # grab the image dimensions
    height = image.shape[0]
    width = image.shape[1]

    # generate a lookup table for center, sigma & gain
    if (center != _last_center or sigma != _last_sigma or gain != _last_gain):
        _update_bandpass_lookup(center, sigma, gain)

    for y in range(0, height):
        for x in range(0, width):
            # pull each component out as a float [0..1]
            ih = image[y, x, 0]
            s = image[y, x, 1] / 255.0
            v = image[y, x, 2] / 255.0

            # map from [0..255] -> [0..1] through lookup table
            # this applies the bandpass filter on hue
            h = _bandpass_lookup[ih]

            # mask the hue with sat, val and apply another gain filter
            f = (h * s * v) * mask_gain
            if f > 1.0:
                f = 1.0

            # covert back to char space
            mask = <unsigned char>(f * 255)
            image[y, x, 0] = mask
            image[y, x, 1] = mask
            image[y, x, 2] = mask

    # return the thresholded image
    return image
