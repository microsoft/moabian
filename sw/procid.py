#!/usr/bin/env python3
import sys, os, time, errno
import psutil
import logging as log
from psutil import Process, signal

def stop_doppelgänger(pid_path='/tmp/menu.pid'):

    if os.path.isfile(pid_path):
        if os.path.isfile(pid_path):
            with open(pid_path, 'r') as f:
                pid = int(f.read())

            try:
                twin = Process(pid)
                twin.send_signal(signal.SIGTERM)
                print(f"our twin {twin.pid} was stopped", flush=True)
                twin.wait(timeout=5)
            except psutil.NoSuchProcess as e:
                pass
            except psutil.TimeoutExpired as e:
                print(f"Timeout expired; exiting.", flush=True)
                sys.exit(10)
            except OSError as e:
                # errno.ESRCH unimportant: sometimes the /tmp/menu.pid is stale
                if e.errno == errno.ESRCH:
                    print(f'no such process which is ok.')
                else:
                    print(f'Unexpected OSError {e}')
            except Exception as e:
                print(f'Unexpected exception {e}')

    this_pid = psutil.Process()
    with open(pid_path, 'w') as f:
        f.write(str(this_pid.pid))
    return this_pid.pid

def setup_signal_handlers():

    # raises SystemExit(0) for controlled shutdown if run under systemd
    # /bin/kill -s TERM $(cat /tmp/menu.pid)
    def handler(signum, stack):
        print(f"Caught {signum}", flush=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)


if __name__ == "__main__":

    #setup_signal_handlers()

    def int_handler(signum, stack):
        print(f"Caught {signum}", flush=True)
        sys.exit(0)

    def term_handler(signum, stack):
        print(f'\nCaught SIGTERM...simulating slow exit in 3.', end='', flush=True)
        for s in range(2,0,-1):
            print(s, end='.', flush=True)
            time.sleep(1)
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, int_handler)

    try:
        mypid = stop_doppelgänger()
        input(f'This pid={mypid}.\nPress any key to quit...')
    finally:
        print("Goodbye")
