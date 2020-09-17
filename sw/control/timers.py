# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Timer classes for profiling
"""

import time
from threading import Thread

from .perfcounters import WindowedAverageCounter
from .perfcounters import PerformanceCounters as counter


# A synchronous, low-drift timer using iterators
# Use this timer for fixed time-step update loops
# https://stackoverflow.com/a/28034554/802203
class BusyTimer:
    def __init__(self):
        self.running = False

    def start(self, period, f, *args):
        def g_tick():
            t = time.perf_counter()
            count = 0
            while self.running:
                count += 1
                yield max(t + count * period - time.perf_counter(), 0)

        self.running = True
        g = g_tick()
        counter.start("loop", WindowedAverageCounter)
        while self.running:
            counter.stop()
            counter.start("loop", WindowedAverageCounter)
            time.sleep(next(g))
            f(*args)
        counter.stop()

    def stop(self):
        self.running = False


# A threaded timer that yields the CPU
# Use this for low frequency operations only
# as it has a larger drift margin than BusyTimer
class ThreadedTimer:
    def __init__(self):
        self.running = False
        self.thread = None

    def __threadCallback(self):
        while self.running:
            if self.callback is not None:
                self.callback(*self.args)
            time.sleep(self.period)

    def start(self, period, f, *args):
        if self.thread:
            raise Exception("Double start()")

        self.period = period
        self.callback = f
        self.args = args

        self.thread = Thread(target=self.__threadCallback)
        self.thread.daemon = True
        self.running = True
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.running = False
            self.thread.join(timeout=self.period)
            self.thread = None
