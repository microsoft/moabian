# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import argparse

from controllers import (
    zero_controller,
    pid_controller,
    brain_controller,
    random_controller,
    manual_controller,
)
from hat import Hat
from enum import Enum
from env import MoabEnv
from hat import Icon, Text
from calibrate import calibrate_all
from log_decorators import logging_decorator


class StateMachine(Enum):
    Menu = 0
    Controller = 1


# These make the respective functions 'act' like controllers
def calibrate_controller(**kwargs):
    calibrate_all(
        kwargs["env"],
        kwargs["pid_fn"],
        kwargs["calibration_file"],
    )
    return lambda state: ((0, 0), {})


def info_screen_controller(**kwargs):
    env.hat.print_info_screen()
    return lambda state: ((0, 0), {})


def main(debug):
    with MoabEnv(frequency=30, debug=debug) as env:
        current = StateMachine.Menu
        index = 0

        # Structure is (controller_closure, icon_inactive, text, kwargs to controller_closure)
        opts_list = [
            (manual_controller, Icon.DOWN, Text.MANUAL, {}),
            (pid_controller, Icon.UP_DOWN, Text.CLASSIC, {}),
            (brain_controller, Icon.UP_DOWN, Text.BRAIN, {"port": 5000}),
            (
                calibrate_controller,
                Icon.UP_DOWN,
                Text.CAL,
                {
                    "env": env,
                    "pid_fn": pid_controller(),
                    "calibration_file": "bot.json",
                },
            ),
            (info_screen_controller, Icon.UP, Text.INFO, {"env": env}),
        ]

        state, detected, buttons = env.reset(Icon.BLANK, Text.BLANK)
        while True:
            if current == StateMachine.Menu:
                while True:
                    _, _, buttons = env.step((0, 0))  # Set/keep plate level
                    env.hat.set_icon_text(opts_list[index][1], opts_list[index][2])

                    if buttons.joy_button:  # Select controller
                        current = StateMachine.Controller
                        break  # Go into the controller loop now
                    elif buttons.joy_y < -0.8:  # Flick joystick down
                        index = min(index + 1, len(opts_list) - 1)
                        time.sleep(0.1)
                    elif buttons.joy_y > 0.8:  # Flick joystick up
                        index = max(index - 1, 0)
                        time.sleep(0.1)

            else:
                state, detected, buttons = env.reset(Icon.DOT, opts_list[index][2])

                # Initialize the controller
                controller_closure = opts_list[index][0]
                kwargs = opts_list[index][3]
                controller = controller_closure(**kwargs)

                while not buttons.menu_button:
                    action, info = controller((state, detected, buttons))
                    state, detected, buttons = env.step(action)

                # Loop breaks after menu pressed
                current = StateMachine.Menu


if __name__ == "__main__":
    # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    args, _ = parser.parse_known_args()
    main(args.debug)
