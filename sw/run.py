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
from log_decorators import log_decorator


CONTROLLER_INFO = {
    "pid": (pid_controller, Icon.DOT, Text.CLASSIC),
    "zero": (zero_controller, Icon.DOT, Text.BLANK),
    "brain": (brain_controller, Icon.DOT, Text.BRAIN),
    "random": (random_controller, Icon.DOT, Text.BLANK),
    "manual": (manual_controller, Icon.DOT, Text.MANUAL),
}

# Seperate each element out into its own dictionary
CONTROLLERS = {key: val[0] for key, val in CONTROLLER_INFO.items()}
ICONS = {key: val[1] for key, val in CONTROLLER_INFO.items()}
TEXTS = {key: val[2] for key, val in CONTROLLER_INFO.items()}


def main(
    controller_name,
    frequency,
    debug,
    max_angle,
    port,
    enable_logging,
    logfile,
    use_plate_angles,
):
    icon = ICONS[controller_name]
    text = TEXTS[controller_name]

    if enable_logging:
        # Pass all arguments, if a controller doesn't need it, it will ignore it (**kwargs)
        controller = logging_decorator(
            CONTROLLERS[controller_name](
                frequency=frequency,
                max_angle=max_angle,
                end_point="http://localhost:" + str(port),
            ),
            logfile=logfile,
        )
    else:
        # Pass all arguments, if a controller doesn't need it, it will ignore it (**kwargs)
        controller = CONTROLLERS[controller_name](
            frequency=frequency,
            max_angle=max_angle,
            end_point="http://localhost:" + str(port),
        )

    with MoabEnv(frequency, debug, use_plate_angles) as env:
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
    parser.add_argument("-f", "--frequency", default=30, type=int)
    parser.add_argument("-ma", "--max_angle", default=16, type=float)
    parser.add_argument("-p", "--port", default=5000, type=int)
    parser.add_argument("-l", "--enable_logging", action="store_true")
    parser.add_argument("-lf", "--logfile", default="/tmp/log.csv", type=str)
    parser.add_argument("-pa", "--use_plate_angles", action="store_true")
    args, _ = parser.parse_known_args()
    main(
        args.controller,
        args.frequency,
        args.debug,
        args.max_angle,
        args.port,
        args.enable_logging,
        args.logfile,
        args.use_plate_angles,
    )
