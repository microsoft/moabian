#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import sys
import time
import yaml
import click
import procid
import logging
import subprocess
import json
import docker

from hat import Icon
from enum import Enum
from env import MoabEnv
from functools import partial
from dataclasses import dataclass
from log_csv import log_decorator
from calibrate import calibrate_controller
from typing import Callable, Any, Union, Optional, List
from procid import setup_signal_handlers, stop_doppelgänger
from info_screen import info_screen_controller, info_config_controller
from controllers import (
    pid_controller,
    zero_controller,
    brain_controller,
    joystick_controller,
    dump_ball_controller,
    BrainNotFound,
)

LOG = logging.getLogger(__name__)


@dataclass
class MenuOption:
    name: str
    closure: Callable
    kwargs: dict
    # Some menu options are controllers (run a control loop), others are simply
    # blocking functions that return on menu press. These other functions are
    # for anything that does something to the bot (displaying info to the screen,
    # doing a calibration, running git pull, etc.)
    is_controller: bool = True
    decorators: Optional[List[Callable]] = None  # List of functions to decorate
    require_servos: bool = True  # To not turn on servos unnecessarily


class MenuState(Enum):
    first_level = 1  # In the main menu screen (selecting beteween menu options)
    second_level = 2  # Inside a controller or 'modal' (running the fn from MenuOption)


def squash_small_angles(controller_fn, min_angle=1.0):
    """
    Decorates a controller that sets actions smaller than a certain angle to 0.
    """
    # Acts like a normal controller function
    def decorated_controller(state):
        action, info = controller_fn(state)  # The actual controller
        (pitch, roll) = action

        if abs(pitch) < min_angle:
            pitch = 0
        if abs(roll) < min_angle:
            roll = 0

        action = (pitch, roll)
        return (action), info

    return decorated_controller


def build_menu(env, log_on, logfile):
    log_csv = lambda fn: log_decorator(fn, logfile)

    top_menu = [
        MenuOption(
            name="Calibrate",
            closure=calibrate_controller,
            kwargs={
                "env": env,
                "pid_fn": pid_controller(),
                "calibration_file": "bot.json",
            },
            is_controller=False,
        ),
        MenuOption(
            name="Joystick",
            closure=joystick_controller,
            kwargs={},
            decorators=[squash_small_angles],
        ),
        MenuOption(
            name="PID",
            closure=pid_controller,
            kwargs={},
            decorators=[log_csv] if log_on else None,
        ),
    ]

    # Parse the docker-compose.yml file for a list of brains
    middle_menu = []
    # Parse brains from docker ps and add to middle_menu
    # parse the list
    for brain_image in docker.ps():
        m = MenuOption(
            name=brain_image.short_name,
            closure=brain_controller,
            kwargs={"port": brain_image.port, "alert_fn": alert_callback},
            decorators=[log_csv] if log_on else none,
        )
        middle_menu.append(m)

    bottom_menu = [
        MenuOption(
            name="Hue Info",
            closure=info_config_controller,
            kwargs={"env": env},
            is_controller=False,
            require_servos=False,
        ),
        MenuOption(
            name="Bot Info",
            closure=info_screen_controller,
            kwargs={"env": env},
            is_controller=False,
            require_servos=False,
        ),
    ]

    return top_menu + middle_menu + bottom_menu


def museum_mode(env, prev_state, dump_angle):
    dump_ball_fn = dump_ball_controller(angle=dump_angle, tilt_angle=5)
    zero_fn = zero_controller()
    state, detected, buttons = prev_state

    # Dump the ball for 1 second
    for _ in range(env.frequency * 1):
        action, _ = dump_ball_fn((state, detected, buttons))
        state, detected, buttons = env.step(action)
        time.sleep(1 / env.frequency)

        if buttons.menu_button:
            return (state, detected, buttons), True

    # Level the plate
    action, _ = zero_fn((state, detected, buttons))
    state, detected, buttons = env.step(action)

    # Disable servos
    env.hardware.disable_servos()
    time.sleep(1 / env.frequency)

    # Wait until the ball is detected again for 3 consecutive frames
    detected_count = 0
    detected = False
    while detected_count < 3:
        action, _ = zero_fn((state, detected, buttons))
        state, detected, buttons = env.step(action)
        time.sleep(1 / env.frequency)

        if detected:
            detected_count += 1
        else:
            detected_count = 0

        if buttons.menu_button:
            env.hardware.enable_servos()
            return (state, detected, buttons), True

    # Re-enable servos
    env.hardware.enable_servos()
    time.sleep(1 / env.frequency)

    return (state, detected, buttons), False


# color list: https://github.com/pallets/click/blob/master/examples/colors/colors.py
out = partial(click.secho, bold=False, err=True)
err = partial(click.secho, fg="red", err=True)


def alert_callback(is_error):
    if is_error:
        err("Brain predict error")


def _handle_debug(ctx, param, debug):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=log_level,
    )
    return debug


@click.command()
@click.version_option(version="3.1.1")
@click.option(
    "-c",
    "--cont",
    type=click.IntRange(-1, 7),
    default=-1,
    help="Default startup controller index",
    show_default=True,
)
@click.option(
    "-d",
    "--debug/--no-debug",
    default=True,
    help="programmer details showing Tx/Rx buffers",
)
@click.option(
    "-f",
    "--file",
    default="/tmp/log.csv",
    help=("If --log, then save CSV to this file"),
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
)
@click.option(
    "-h",
    "--hertz",
    type=click.IntRange(1, 40),
    default=30,
    help="Frequency of controller in Hz",
    show_default=True,
)
@click.option(
    "-l",
    "--log/--no-log",
    default=True,
    help=("Enables or disables the logging as specified by -f/--file"),
)
@click.option("-r", "--reset/--no-reset", help="Reset Moab firmware on start")
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=1,
    help="verbose tx/rx (-v=OLED changes, -vv=servo commands, -vvv=NOOPs)",
)
@click.option(
    "--museum/--no-museum",
    default=False,
    help=(
        "Enables the museum mode. "
        "Exit controllers after a set time and dump the ball towards one side"
    ),
)
@click.option(
    "--museum-timeout",
    type=int,
    default=300,  # 5 minutes
    help="Timeout before museum mode is enabled (in seconds)",
)
@click.option(
    "--museum-dump-angle",
    type=click.IntRange(0, 360),
    default=90,
    help="Angle to dump the ball towards in museum mode",
)
@click.pass_context
def main(ctx: click.core.Context, **kwargs: Any) -> None:
    if kwargs["verbose"] == 2:
        err(f"Starting {sys.argv[0]}")
        out(f"Starting {kwargs}")

    main_menu(**kwargs)


def main_menu(
    cont,
    debug,
    file,
    hertz,
    log,
    reset,
    verbose,
    museum,
    museum_dump_angle,
    museum_timeout,
):

    if reset:
        out("Resetting firmware")
        os.system("raspi-gpio set 6 dh && sleep 0.05 && raspi-gpio set 6 dl")

    with MoabEnv(hertz, debug=debug, verbose=verbose) as env:
        menu_list = build_menu(env, log, file)

        if cont == -1:
            # normal startup state
            current = MenuState.first_level
            index = 0
            last_index = -1
        else:
            # CLI argument to start in one of the controllers
            current = MenuState.second_level
            index = cont
            last_index = -1

        # Default menu raises the plate to alert the user the system is ready
        if cont == -1:
            env.hardware.enable_servos()
            env.hardware.go_up()
            buttons = env.hardware.get_buttons()
            env.hardware.disable_servos()

        while True:
            time.sleep(1 / env.frequency)

            # In the first level of the menu (select between menu options)
            if current == MenuState.first_level:
                # Depends on if it's the first/last icon
                if index == 0:
                    icon = Icon.DOWN
                elif index == len(menu_list) - 1:
                    icon = Icon.UP
                else:
                    icon = Icon.UP_DOWN

                # Only update text and icon if it has changed
                if last_index != index:
                    env.hardware.display(menu_list[index].name, icon)
                    last_index = index

                buttons = env.hardware.get_buttons()
                if buttons.joy_button:  # Enter the menu option
                    current = MenuState.second_level
                elif buttons.joy_y < -0.8:  # Flick joystick down
                    index = min(index + 1, len(menu_list) - 1)
                    time.sleep(0.1)
                elif buttons.joy_y > 0.8:  # Flick joystick up
                    # "Pull to refresh"
                    # If you go above the top of the menu, refresh the menu list
                    if index == 0:
                        menu_list = build_menu(env, log, file)
                        env.hardware.display("Refreshing", icon.BLANK)
                        time.sleep(0.5)
                        env.hardware.display(menu_list[index].name, icon)

                    index = max(index - 1, 0)
                    time.sleep(0.1)

            else:  # current == MenuState.second_level:
                if menu_list[index].require_servos:
                    env.hardware.enable_servos()

                # Reset the controller
                if menu_list[index].is_controller:
                    state, detected, buttons = env.reset(
                        menu_list[index].name, Icon.DOT
                    )

                # Initialize the controller
                controller_closure = menu_list[index].closure
                kwargs = menu_list[index].kwargs
                controller = controller_closure(**kwargs)

                # Wrap a decorator if it has one
                if menu_list[index].decorators:
                    for decorator in menu_list[index].decorators:
                        controller = decorator(controller)

                # Ensure there's enough time to process the display command on
                # the hat side (if a control command happens too soon after a
                # display command the hat may not have enough time to read the
                # next command, which will mess with SPI)
                time.sleep(1 / env.frequency)

                if menu_list[index].is_controller:
                    controller_start_time = time.time()

                    # If it's a controller run the control loop
                    try:
                        while not buttons.menu_button:
                            action, info = controller((state, detected, buttons))
                            state, detected, buttons = env.step(action)

                            # If the controller has been running for more than
                            # museum_timeout seconds, exit, and dump the ball towards
                            # one side and wait until the ball is detected again
                            if museum:
                                if time.time() - controller_start_time > museum_timeout:
                                    prev_state = (state, detected, buttons)
                                    next_state, museum_exit = museum_mode(
                                        env, prev_state, museum_dump_angle
                                    )
                                    state, detected, buttons = next_state
                                    controller_start_time = time.time()
                                    # Whether the menu button was pressed in museum mode
                                    if museum_exit:
                                        break

                    except BrainNotFound:
                        print(f"caught BrainNotFound in loop")

                    env.hardware.go_up()
                else:
                    # If not a controller, let it do it's own thing. We assume
                    # it's a blocking call that will return when menu is pressed
                    controller()

                # Loop breaks after menu pressed and puts the plate back to go_up
                current = MenuState.first_level
                last_index = -1

                if menu_list[index].require_servos:
                    env.hardware.disable_servos()


if __name__ == "__main__":

    setup_signal_handlers()
    stop_doppelgänger()

    try:
        main(standalone_mode=False)
    except click.Abort:
        sys.stderr.write("Stopping.\n")
        sys.exit(1)
