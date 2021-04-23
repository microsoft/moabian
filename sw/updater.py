# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import subprocess
import time


def update_controller(env, **kwargs):
    subprocess.run(["git", "pull"])
    subprocess.run(["/home/pi/moab/bin/restart"])

    def wait_for_menu():
        menu_button = False
        while not menu_button:
            time.sleep(1 / env.frequency)
            env.hat.noop()
            menu_button, joy_button, joy_x, joy_y = env.hat.get_buttons()

    return wait_for_menu
