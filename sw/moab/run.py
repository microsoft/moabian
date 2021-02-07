import argparse

from controllers import (
    zero_controller,
    pid_controller,
    brain_controller,
    manual_controller,
)
from hat import Icon, Text
from env import MoabEnv
from hat import Hat


ICONS = {
    "pid": Icon.DOT,
    "zero": Icon.DOT,
    "brain": Icon.DOT,
    "manual": Icon.DOT,
}

TEXTS = {
    "pid": Text.CLASSIC,
    "zero": Text.BLANK,
    "brain": Text.BRAIN,
    "manual": Text.MANUAL,
}

CONTROLLERS = {
    "pid": pid_controller,
    "zero": zero_controller,
    "brain": brain_controller,
    "manual": manual_controller,
}


def main(controller_name, frequency, debug, max_angle):
    # Only manual needs access to the hat outside of the env
    hat = Hat()

    icon = ICONS[controller_name]
    text = TEXTS[controller_name]
    controller = CONTROLLERS[controller_name](
        frequency=frequency, hat=hat, max_angle=max_angle
    )

    with MoabEnv(hat, frequency, debug) as env:
        state = env.reset(icon, text)
        while True:
            action = controller(state)
            state = env.step(action)


if __name__ == "__main__":
    # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--controller",
        default="zero",
        choices=list(CONTROLLERS.keys()),
        help=f"""Select what type of action to take.
        Options are: {CONTROLLERS.keys()}
        """,
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-f", "--frequency", default="30", type=int)
    parser.add_argument("-ma", "--max_angle", default="16", type=float)
    # parser.add_argument("-q", "--image_quality", default="70", type=int, help="[1-100]")  # TODO: add this
    args, _ = parser.parse_known_args()
    main(args.controller, args.frequency, args.debug, args.max_angle)
