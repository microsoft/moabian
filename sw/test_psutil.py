import psutil
import time

with open('/tmp/menu.pid') as f:
    other_pid = int(f.read())

p = psutil.Process(other_pid)
#p.send_signal(psutil.signal.SIGINT)
p.send_signal(psutil.signal.SIGTERM)

try:
    p.wait(timeout=1)
    print("finished, all good")
except TimeoutExpired as exp:
    print("out of time")
