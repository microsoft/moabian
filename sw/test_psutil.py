# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import psutil

with open("/tmp/menu.pid", "r") as f:
    other_pid = int(f.read())

p = psutil.Process(other_pid)
p.send_signal(psutil.signal.SIGINT)
# p.send_signal(psutil.signal.SIGTERM)

try:
    p.wait(timeout=10)
    print("finished, all good")
except TimeoutExpired as exp:
    print("out of time")
