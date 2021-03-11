#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import time
import click

from hat import Icon
from env import MoabEnv
from common import Buttons
from typing import Callable
from functools import partial
from dataclasses import dataclass
from calibrate import run_calibration
from info_screen import info_screen_controller, info_config_controller
from controllers import pid_controller, brain_controller, joystick_controller


# TODO: move to controllers?
def calibrate_controller(**kwargs):
    run_calibration(
        kwargs["env"],
        kwargs["pid_fn"],
        kwargs["calibration_file"],
    )
    return lambda state: ((0, 0), {})


# color list: https://github.com/pallets/click/blob/master/examples/colors/colors.py
out = partial(click.secho, bold=False, err=True)
err = partial(click.secho, fg="red", err=True)


@dataclass
class Mode:
    verbose: int
    debug: bool
    frequency: int
    stream: bool
    logfile: str
    controller: str


@dataclass
class ControllerInfo:
    name: str
    closure: Callable
    kwargs: dict


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
    "-d",
    "--debug/--no-debug",
    default=True,
    help="programmer details showing Tx/Rx buffers"
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
def main(ctx, verbose, debug, frequency, stream, logfile, controller):

    if logfile:
        click.echo(click.format_filename(logfile))

    mode = Mode(
        verbose=verbose,
        debug=debug,
        frequency=frequency,
        stream=stream,
        logfile=logfile,
        controller=controller,
    )

    if mode.verbose:
        click.secho(str(mode), fg="green")

    with MoabEnv(frequency, debug=debug) as env:
        current = 1
        index = 0

        opts_list = [
            ControllerInfo("Joystick", joystick_controller, {}),
            ControllerInfo("PID", pid_controller, {}),
            ControllerInfo("Brain", brain_controller, {"port": 5000}),
            ControllerInfo("Custom1", brain_controller, {"port": 5001}),
            ControllerInfo("Custom2", brain_controller, {"port": 5002}),
            ControllerInfo(
                "Calibrate",
                calibrate_controller,
                {
                    "env": env,
                    "pid_fn": pid_controller(),
                    "calibration_file": "bot.json",
                },
            ),
            ControllerInfo("Calib Info", info_config_controller, {"env": env}),
            ControllerInfo("Bot Info", info_screen_controller, {"env": env}),
        ]

        env.hat.hover()
        buttons = env.hat.get_buttons()
        while True:
            time.sleep(1 / env.frequency)

            if current == 1:
                # Depends on if it's the first/last icon
                if index == 0:
                    icon = Icon.DOWN
                elif index == len(opts_list) - 1:
                    icon = Icon.UP
                else:
                    icon = Icon.UP_DOWN

                env.hat.display_string_icon(opts_list[index].name, icon)
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
                    state, detected, buttons = env.reset(
                        opts_list[index].name, Icon.DOT
                    )

                # Initialize the controller
                controller_closure = opts_list[index].closure
                kwargs = opts_list[index].kwargs
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
