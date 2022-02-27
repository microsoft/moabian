# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse

from env import MoabEnv
from hat import Hat, Icon
from controllers import pid_controller, brain_controller, joystick_controller


CONTROLLERS = {
    "PID": pid_controller,
    "Brain": brain_controller,
    "Joystick": joystick_controller,
}

ICONS = {
    "PID": Icon.DOT,
    "Brain": Icon.DOT,
    "Joystick": Icon.DOT,
}


def main(controller_name, frequency, debug, max_angle, port):
    icon = ICONS[controller_name]

    # Pass all arguments, if a controller doesn't need it, it will ignore it (**kwargs)
    controller_fn = CONTROLLERS[controller_name]
    controller = controller_fn(
        frequency=frequency,
        max_angle=max_angle,
        end_point="http://localhost:" + str(port),
    )

    with MoabEnv(frequency, debug) as env:
        state, _, _, env_info = env.reset(text=controller_name, icon=ICONS[controller_name])
        while True:
            action, ctrl_info = controller(state, env_info)
            state, _, _, env_info = env.step(action)
            print(state, action)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--controller",
        default="PID",
        choices=list(CONTROLLERS.keys()),
        help=f"""Select what type of action to take.
        Options are: {CONTROLLERS.keys()}
        """,
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-f", "--frequency", default="30", type=int)
    parser.add_argument("-ma", "--max_angle", default="16", type=float)
    parser.add_argument("-p", "--port", default=5000, type=int)
    args, _ = parser.parse_known_args()
    main(
        args.controller,
        args.frequency,
        args.debug,
        args.max_angle,
        args.port,
    )
