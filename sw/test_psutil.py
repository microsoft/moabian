import psutil
import time

p = psutil.Process(4856)
p.send_signal(psutil.signal.SIGINT)

try:
    p.wait(timeout=1)
    print("finished, all good")
except TimeoutExpired as exp:
    print("out of time")
