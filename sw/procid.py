#!/usr/bin/env python3
import sys, os, signal, time, errno
import psutil
import logging as log

def kill_doppelganger(pid_path='/tmp/menu.pid'):
    my_pid=os.getpid()

    if os.path.isfile(pid_path):
        with open(pid_path, 'r') as f:
            other_pid = int(f.read())
            try:
                print(f'Sending SIGINT to {other_pid}...', end='')
                os.kill(other_pid, signal.SIGINT)
                print(f'sent.')
            except OSError as err:
                if err.errno == errno.ESRCH:
                    print(f'no such process.')
                else:
                    print(f'oserror {err}')
            except Exception as e:
                print(f'Unexpected exception {e} which is ok')

    with open(pid_path, 'w') as f:
        f.write(str(my_pid))
    return my_pid

def sigterm_handler(_signum, _stack_frame):
    # Raises SytemExit(0)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        pid = kill_doppelganger()
        input(f'This pid={pid}. Press any key to quit...')
    except KeyboardInterrupt:
        print(f'\nCaught SIGINT...exiting in ', end='', flush=True)
        for s in range(3,0,-1):
            print(s, end='.', flush=True)
            time.sleep(1)
        sys.exit(-signal.SIGINT)
    finally:
        print("Goodbye")
