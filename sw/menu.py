#!/usr/bin/env python3

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
from enum import Enum
from env import MoabEnv
from log_csv import log_decorator
from calibrate import run_calibration
from common import EnvState, Buttons
from hat import Hat, Icon, Text, _get_host_ip, _get_sw_version


class StateMachine(Enum):
    Menu = 0
    Controller = 1


# These make the respective functions 'act' like controllers
def calibrate_controller(**kwargs):
    run_calibration(
        kwargs["env"],
        kwargs["pid_fn"],
        kwargs["calibration_file"],
    )
    return lambda state: ((0, 0), {})


def info_screen_controller(env=None, **kwargs):
    env.hat.print_info_screen()
    return lambda state: ((0, 0), {})


def main(frequency=30, debug=True):

    with MoabEnv(frequency, debug) as env:
        current = StateMachine.Menu
        index = 0

        # Structure is (controller_closure, icon_inactive, text, kwargs to controller_closure)
        opts_list = [
            (info_screen_controller, Icon.DOWN, Text.INFO, {"env": env}),
            (manual_controller, Icon.UP_DOWN, Text.MANUAL, {}),
            (pid_controller, Icon.UP_DOWN, Text.CLASSIC, {}),
            (brain_controller, Icon.UP_DOWN, Text.BRAIN, {"port": 5000}),
            (
                calibrate_controller,
                Icon.UP,
                Text.CAL,
                {
                    "env": env,
                    "pid_fn": pid_controller(),
                    "calibration_file": "bot.json",
                },
            ),
        ]

        env.hat.hover()
        buttons = env.hat.get_buttons()
        while True:
            time.sleep(1 / env.frequency)
            if current == StateMachine.Menu:
                # TOP LEVEL
                env.hat.set_icon_text(opts_list[index][1], opts_list[index][2])
                env.hat.noop()
                buttons = env.hat.get_buttons()

                if buttons.joy_button:  # Selected controller
                    current = StateMachine.Controller
                elif buttons.joy_y < -0.8:  # Flicked joystick down
                    index = min(index + 1, len(opts_list) - 1)
                elif buttons.joy_y > 0.8:  # Flicked joystick up
                    index = max(index - 1, 0)

            else:
                # SECOND LEVEL
                if index == 0 or index == 4:
                    state = (0, 0, 0, 0, 0, 0)
                    detected = False
                    buttons = Buttons()
                else:
                    state, detected, buttons = env.reset(Icon.DOT, opts_list[index][2])

                # Initialize the controller
                controller_closure = opts_list[index][0]
                kwargs = opts_list[index][3]
                controller = controller_closure(**kwargs)

                while not buttons.menu_button:
                    action, info = controller((state, detected, buttons))
                    state, detected, buttons = env.step(action)

                # Loop breaks after menu pressed and puts the plate back to hover
                current = StateMachine.Menu
                env.hat.hover()


if __name__ == "__main__":
    # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-f", "--frequency", default="30", type=int)
    args, _ = parser.parse_known_args()
    main(args.frequency, args.debug)
