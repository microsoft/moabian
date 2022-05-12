import curses
import os
from curses import wrapper
from hardware import MoabHardware
import json
import time

def write_calibration(calibration_dict, calibration_file="bot.json"):
    with open(calibration_file, "w+") as outfile:
        json.dump(calibration_dict, outfile, indent=4, sort_keys=True)

def read_calibration(calibration_file="bot.json"):
    if os.path.isfile(calibration_file):
        with open(calibration_file, "r") as f:
            calibration_dict = json.load(f)
    else:  # Use defaults
        calibration_dict = {
            "ball_hue": 44,
            "plate_offsets": (0.0, 0.0),
            "servo_offsets": (0.0, 0.0, 0.0),
        }
    return calibration_dict

def tabular(v):
    return " ".join(map("{: >4}".format, v))

def hw_to_user(vector):
    v1 = [x * -1 for x in vector]
    t = v1[0]
    v1[0] = v1[1]
    v1[1] = t
    return v1
    

def drawtext(scr, vector, status):
    scr.addstr(0, 0, tabular("uio▲"))
    scr.addstr(1, 0, tabular(hw_to_user(vector)), curses.color_pair(1))
    scr.addstr(2, 0, tabular("jkl▼"))
    scr.addstr(4, 0, status, curses.color_pair(2))

def main(scr):
    rc = read_calibration()
    s = read_calibration()["servo_offsets"]
    s = list(map(int, s))
    status = f"bot.json offsets: {hw_to_user(s)}"

    with MoabHardware() as hw:

        curses.noecho()         # don't echo keypress
        curses.curs_set(0)      # make cursor invisible
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        hw.enable_servos()
        hw.go_up()

        key = None
        while True:
            scr.clear()
            drawtext(scr, s, status)

            hw.servo_offsets = s
            hw.display(str(hw_to_user(hw.servo_offsets)))
            hw.set_angles(0, 0)

            scr.refresh()
            key = scr.getkey()

            if key == "u" or key == "KEY_IC":
                s[1] -= 1
            if key == "j" or key == "KEY_DC":
                s[1] += 1

            if key == "i" or key == "KEY_HOME":
                s[0] -= 1
            if key == "k" or key == "KEY_END":
                s[0] += 1

            if key == "o" or key == "KEY_PPAGE":
                s[2] -= 1
            if key == "l" or key == "KEY_NPAGE":
                s[2] += 1

            if key == "p" or key == " ":
                hw.set_servos(145,145,145)
                time.sleep(0.1)
                hw.set_angles(0,0)
                time.sleep(0.1)
                status = "recycle"


            if key == "r":
                s = [0, 0, 0]
                status = "Reset to [0,0,0]"

            if key == "s" or key == "w":
                c = read_calibration()
                c["servo_offsets"] = s
                write_calibration(c)
                status = f"New offsets saved {hw_to_user(s)}"

            if key == "" or key == 'q':
                break


wrapper(main)

