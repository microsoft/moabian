# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse

from controllers import (
    zero_controller,
    pid_controller,
    brain_controller,
    random_controller,
    manual_controller,
)
from hat import Hat
from env import MoabEnv
from hat import Icon, Text


CONTROLLERS = {
    "pid": pid_controller,
    "zero": zero_controller,
    "brain": brain_controller,
    "random": random_controller,
    "manual": manual_controller,
}

ICONS = {
    "pid": Icon.DOT,
    "zero": Icon.DOT,
    "brain": Icon.DOT,
    "random": Icon.DOT,
    "manual": Icon.DOT,
}

TEXTS = {
    "pid": Text.CLASSIC,
    "zero": Text.BLANK,
    "brain": Text.BRAIN,
    "random": Text.BLANK,
    "manual": Text.MANUAL,
}


def main(controller_name, frequency, debug, max_angle, port):
    icon = ICONS[controller_name]
    text = TEXTS[controller_name]

    # Pass all arguments, if a controller doesn't need it, it will ignore it (**kwargs)
    controller_fn = CONTROLLERS[controller_name]
    controller = controller_fn(
        frequency=frequency,
        max_angle=max_angle,
        end_point="http://localhost:" + str(port),
    )

    with MoabEnv(hat, frequency, debug) as env:
        state = env.reset(icon, text)
        while True:
            action, info = controller(state)
            state = env.step(action)


if __name__ == "__main__":
    # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--controller",
        default="pid",
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
