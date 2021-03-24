#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import time
import click
import procid
import logging
import yaml

from procid import *
from hat import Icon
from enum import Enum
from env import MoabEnv
from typing import Callable, Any, Union
from functools import partial
from dataclasses import dataclass
from log_csv import log_decorator
from calibrate import calibrate_controller
from info_screen import info_screen_controller, info_config_controller
from controllers import pid_controller, brain_controller, joystick_controller

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
    is_controller: bool
    require_servos: bool = True  # To not turn on servos unnecessarily


class MenuState(Enum):
    first_level = 1  # In the main menu screen (selecting beteween menu options)
    second_level = 2  # Inside a controller or 'modal' (running the fn from MenuOption)


def update_icon_fn(hat):
    def update_icon(toggle: bool):
        print(f"Alert: brain threw an error")

    return update_icon

def getFromDict(dataDict, mapList):
    for k in mapList: dataDict = dataDict[k]
    return dataDict
   
def build_menu_list(env):
    menu_name = ""
    port = 0
    top_part = [
        MenuOption(
            name="Joystick",
            closure=joystick_controller,
            kwargs={},
            is_controller=True,
        ),
        MenuOption(
            name="PID",
            closure=pid_controller,
            kwargs={},
            is_controller=True,
        ),
        ]
    custom_menu_list = []
    bottom_part = [
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
            name="Hue",
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
    dc_file = "../docker-compose.yml"

    if os.path.isfile(dc_file):
        with open(dc_file, 'r') as ymlfile:
            docker_compose = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
        # limit to services node in docker compose
        services = getFromDict(docker_compose,["services"])
        
        for service, info in services.items():
            
            #split out port
            splitports = info['ports']
            ports = splitports[0].split(":")
            port = ports[0]

            # if container name exists, use it, else use image name
            if "container_name" in info.keys():
                menu_name = info['container_name']  
            else:
                slashes = info['image'].split("/")
                #if image tag or no slashes, use the image name 
                if slashes is not None and len(slashes) == 1:
                    menu_name = info['image']
                else:
                    colon = slashes[-1].split(":")
                    menu_name = colon[0]
                     

            menuOption = MenuOption(menu_name, brain_controller,{"port": port},True)
            custom_menu_list.append(menuOption)

        menu_list = top_part + custom_menu_list + bottom_part
        return menu_list


def get_menu_list(env):
    update_icon = update_icon_fn(env.hat)
    menu_list = build_menu_list(env)
    return menu_list
    
    """ [
        MenuOption(
            name="Joystick",
            closure=joystick_controller,
            kwargs={},
            is_controller=True,
        ),
        MenuOption(
            name="PID",
            closure=pid_controller,
            kwargs={},
            is_controller=True,
        ),
        MenuOption(
            name="Brain",
            closure=brain_controller,
            kwargs={"port": 5000},
            is_controller=True,
        ),
        MenuOption(
            name="Custom1",
            closure=brain_controller,
            kwargs={"port": 5001},
            is_controller=True,
        ),
        MenuOption(
            name="Custom2",
            closure=brain_controller,
            kwargs={"port": 5002},
            is_controller=True,
        ),
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
            name="Hue",
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
    ] """


# color list: https://github.com/pallets/click/blob/master/examples/colors/colors.py
out = partial(click.secho, bold=False, err=True)
err = partial(click.secho, fg="red", err=True)

def _handle_debug(ctx, param, debug):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=log_level,
    )
    return debug

# -c controller
# -d debug
# -f logfile
# -h hertz
# -l log on/off
# -v verbose

@click.command()
@click.version_option(version="3.0.21")
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
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=1,
    help="verbose tx/rx (1=OLED changes, 2=servo commands, 3=NOOPs)"
)
@click.pass_context
def main(ctx: click.core.Context, **kwargs: Any) -> None:
    if kwargs["verbose"] == 2:
        err(f"Starting {sys.argv[0]}")
        out(f"Starting {kwargs}")

    main_menu(**kwargs)


def main_menu(cont, debug, file, hertz, log, verbose):

    with MoabEnv(hertz, debug=debug, verbose=verbose) as env:
        menu_list = get_menu_list(env)

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


        # Default menu raises the servo to alert the user the system is ready
        if cont == -1:
            env.hat.enable_servos()
            env.hat.hover()
            buttons = env.hat.get_buttons()
            time.sleep(1 / env.frequency)
            env.hat.disable_servos()

        while True:
            time.sleep(1 / env.frequency)

            if current == MenuState.first_level:
                # Depends on if it's the first/last icon
                if index == 0:
                    icon = Icon.DOWN
                elif index == len(menu_list) - 1:
                    icon = Icon.UP
                else:
                    icon = Icon.UP_DOWN

                if last_index != index:
                    env.hat.display_string_icon(menu_list[index].name, icon)
                    last_index = index

                # Noop is needed since display string only sends msg when it has
                # a new string (different from previous string)
                env.hat.noop()
                buttons = env.hat.get_buttons()

                if buttons.joy_button:  # Selected controller
                    current = MenuState.second_level
                elif buttons.joy_y < -0.8:  # Flicked joystick down
                    index = min(index + 1, len(menu_list) - 1)
                    time.sleep(0.1)
                elif buttons.joy_y > 0.8:  # Flicked joystick up
                    index = max(index - 1, 0)
                    time.sleep(0.1)

            else:  # current == MenuState.second_level:
                if menu_list[index].require_servos:
                    # Turn on the servos
                    env.hat.enable_servos()

                # Reset the controller
                if menu_list[index].is_controller:
                    state, detected, buttons = env.reset(
                        menu_list[index].name, Icon.DOT
                    )

                # Initialize the controller
                controller_closure = menu_list[index].closure
                kwargs = menu_list[index].kwargs
                if log and menu_list[index].is_controller:  # Use the log decorator
                    controller = log_decorator(
                        controller_closure(**kwargs), logfile=file
                    )
                else:
                    controller = controller_closure(**kwargs)

                # Ensure there's enough time to process the display command on
                # the hat side (if a control command happens too soon after a
                # display command the hat may not have enough time to read the
                # next command, which will mess with SPI)
                time.sleep(1 / env.frequency)

                if menu_list[index].is_controller:
                    # If it's a controller run the control loop
                    while not buttons.menu_button:
                        action, info = controller((state, detected, buttons))
                        state, detected, buttons = env.step(action)

                    env.hat.hover()
                else:
                    # If not a controller, let it do it's own thing. We assume
                    # it's a blocking call that will return when menu is pressed
                    controller()

                # Loop breaks after menu pressed and puts the plate back to hover
                current = MenuState.first_level
                last_index = -1

                if menu_list[index].require_servos:
                    # Turn off the servos for main menu (they make that crackling noise)
                    env.hat.disable_servos()



if __name__ == "__main__":

    setup_signal_handlers()
    stop_doppelgänger()

    try:
        main(standalone_mode=False)
    except click.Abort:
        sys.stderr.write("Stopping.\n")
        sys.exit(1)
