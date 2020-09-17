# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Performance counters
"""

import time
import logging as log
from enum import Enum
from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional


class Evolution(Enum):
    Sample = 0
    CumulativeMovingAverage = 1
    WindowedAverage = 2
    FPSCounter = 3


@dataclass
class TimingContext:
    name: str
    startTime: float
    evolution: type


class CounterBase:
    def update(self, value: float):
        pass


class SamplingCounter(CounterBase):
    """
    Show the most recent value.
    """

    def __init__(self):
        self.value: float = 0.0

    def update(self, value: float):
        self.value = value


class FrequencyCounter(CounterBase):
    """
    Do a frequency count.

    call counter.update(1) to add one.
    call counter.update(0) to add none.
    """

    def __init__(self):
        self.value: float = 0.0
        self.count: float = 0.0
        self.time_window = 1.0
        self.t_start = time.perf_counter()

    def update(self, value: float):
        t_now = time.perf_counter()
        if t_now - self.t_start > self.time_window:
            self.value = self.count
            self.count = 0.0
            self.t_start = t_now

        self.count += value


class CumulativeMovingAverageCounter(CounterBase):
    """
    Do a moving average of the updated values.
    """

    def __init__(self):
        self.value: float = 0.0
        self.count: int = 0

    def update(self, value: float):
        if self.count is 0:
            self.value = value
        else:
            self.value = (value + self.count * self.value) / (self.count + 1)
        self.count += 1


class WindowedAverageCounter(CounterBase):
    """
    Do windowed average of the updated values.
    """

    def __init__(self, window: int = 10):
        self.deque = deque(maxlen=window)
        self.value: float = 0.0

    def update(self, value: float):
        self.deque.append(value)
        self.value = sum(self.deque) / len(self.deque)


class PerfCounters:
    _instance: Optional["PerfCounters"] = None

    # def __new__(cls, *args, **kwargs):
    #     # Singleton pattern. Insure we only ever get one of these per module load.
    #     if cls._instance is None:
    #         cls._instance = super(PerfCounters, cls).__new__(cls)
    #     return cls._instance

    def __init__(self):
        self.contextStack: Deque[TimingContext] = deque()
        self.counters = {}

    def start(self, context: str, evolution: type, **kwArgs):
        self.contextStack.append(TimingContext(context, time.perf_counter(), evolution))

    def stop(self):
        context = self.contextStack.pop()
        elapsedSec = time.perf_counter() - context.startTime
        counter = self.counters.get(context.name, None)
        if counter is None:
            counter = context.evolution()
            self.counters[context.name] = counter

        self.counters[context.name].update(elapsedSec)

    def update(self, context_name: str, value: float, context_evolution: type):
        """
        Do a single update. Useful for counters which don't start/stop
        """
        counter = self.counters.get(context_name, None)
        if counter is None:
            counter = context_evolution()
            self.counters[context_name] = counter

        self.counters[context_name].update(value)

    def logCounters(self, *names, level: int = log.INFO):
        global perf_logger

        message = ""
        for name in names:
            counter = self.counters.get(name, None)
            if counter is not None:
                message += f"{name}: {counter.value:.3f} "
        perf_logger.log(level, message)

    def logAllCounters(self, level: int = log.INFO):
        global perf_logger

        message = ""
        for name, counter in self.counters.items():
            if counter is not None:
                message += f"{name}: {counter.value:.3f} "
        perf_logger.log(level, message)


perf_logger = log.getLogger("performance")
perf_logger.propagate = False
PerformanceCounters = PerfCounters()
