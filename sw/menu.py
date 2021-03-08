#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import time
import click

#from statemachine import StateMachine
from enum import Enum
from functools import partial

import common, hat, calibrate
from controllers import *
from env import *


# TODO: move to controllers?
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


# color list: https://github.com/pallets/click/blob/master/examples/colors/colors.py
out = partial(click.secho, bold=False, err=True)
err = partial(click.secho, fg="red", err=True)


@dataclass
class Mode:
    verbose: int
    frequency: int
    stream: bool
    logfile: str
    controller: str


@click.command()
@click.version_option(version="3.0")
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="level of verbosity",
)
@click.option(
    "-f",
    "--frequency",
    type=click.IntRange(1, 40),
    default=30,
    help="Cycle time of controller in Hz",
    show_default=True,
)
@click.option(
    "-s",
    "--stream/--no-stream",
    default=True,
    help=("Stream a live view of the camera to http://moab.local"),
)
@click.option(
    "-l",
    "--logfile",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
)
@click.argument("controller", nargs=-1)
@click.pass_context
def main(ctx, verbose, frequency, stream, logfile, controller):

    if logfile:
        click.echo(click.format_filename(logfile))

    mode = Mode(
        verbose=verbose,
        frequency=frequency,
        stream=stream,
        logfile=logfile,
        controller=controller,
    )

    if mode.verbose:
        click.secho(str(mode), fg="green")

    with MoabEnv(frequency, debug=True) as env:
        current = 1
        index = 0

        # Structure is (controller_closure, icon_inactive, text, kwargs to controller_closure)
        opts_list = [
            (
                joystick_controller,
                Icon.DOWN,
                Text.MANUAL,
                {},
            ),
            (
                pid_controller,
                Icon.UP_DOWN,
                Text.CLASSIC,
                {},
            ),
            (
                brain_controller,
                Icon.UP_DOWN,
                Text.BRAIN,
                {"port": 5000},
            ),
            (
                brain_controller,
                Icon.UP_DOWN,
                Text.CUSTOM1,
                {"port": 5001},
            ),
            (
                brain_controller,
                Icon.UP_DOWN,
                Text.CUSTOM2,
                {"port": 5002},
            ),
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
            (
                info_screen_controller,
                Icon.UP,
                Text.INFO,
                {"env": env},
            ),
        ]

        env.hat.hover()
        buttons = env.hat.get_buttons()
        while True:
            time.sleep(1 / env.frequency)

            if current == 1:
                # TOP LEVEL
                env.hat.set_icon_text(
                    opts_list[index][1],
                    opts_list[index][2],
                )
                env.hat.noop()
                buttons = env.hat.get_buttons()

                if buttons.joy_button:  # Selected controller
                    current = 2
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
                current = 1
                env.hat.hover()


if __name__ == "__main__":
    try:
        main(standalone_mode=False)
    except click.Abort:
        sys.stderr.write("Stopping.\n")
        sys.exit(1)
