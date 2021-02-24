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
from calibrate import calibrate_all
from hat import Hat, Icon, Text, _get_host_ip, _get_sw_version


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


def info_screen_controller(env=None, **kwargs):
    ip1, ip2, ip3, ip4 = _get_host_ip()
    env.hat.print_arbitrary_string(f"IP ADDRESS:\n{ip1}.{ip2}.{ip3}.{ip4}")
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
            # (
            #     calibrate_controller,
            #     Icon.UP_DOWN,
            #     Text.CAL,
            #     {
            #         "env": env,
            #         "pid_fn": pid_controller(),
            #         "calibration_file": "bot.json",
            #     },
            # ),
            # (info_screen_controller, Icon.UP, Text.INFO, {"env": env}),
        ]

        env.hat.hover()
        buttons = env.hat.poll_buttons()
        while True:
            # time.sleep(1 / 30)
            if current == StateMachine.Menu:
                # Set icon and text, and get buttons
                env.hat.set_icon_text(opts_list[index][1], opts_list[index][2])
                env.hat.noop()
                buttons = env.hat.poll_buttons()

                if buttons.joy_button:  # Selected controller
                    current = StateMachine.Controller
                elif buttons.joy_y < -0.9:  # Flicked joystick down
                    index = min(index + 1, len(opts_list) - 1)
                    time.sleep(0.2)
                elif buttons.joy_y > 0.9:  # Flicked joystick up
                    index = max(index - 1, 0)
                    time.sleep(0.2)

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
    args, _ = parser.parse_known_args()
    main(args.debug)
