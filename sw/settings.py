# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import json


DEFAULT_SETTINGS = {
    "serial_number": 0,
    "ball_hue": 44,
    "ball_color": "orange",
    "plate_offsets": (0.0, 0.0),
    "servo_offsets": (0.0, 0.0, 0.0),
    "kiosk": False,
    "kiosk_timeout": 15,
    "kiosk_clock_position": 2,
    "servo_safety": False,
    "servo_safety_timeout": 900,
    "servo_safety_clock_position": 2,
}


def get_settings(settings_file="bot.json"):
    # Get calibration settings
    if os.path.isfile(settings_file):
        with open(settings_file, "r") as f:
            settings_dict = json.load(f)

    else:  # Use defaults
        settings_dict = DEFAULT_SETTINGS.copy()
        set_settings(settings_dict, settings_file)

    return settings_dict


def set_settings(settings_dict, settings_file="bot.json"):
    # Write the default calibration file if it didn't exist before
    with open(settings_file, "w") as f:
        json.dump(settings_dict, f, indent=4)


def update_setting(setting_name, setting_value, settings_file="bot.json"):
    settings_dict = get_settings(settings_file)
    settings_dict[setting_name] = setting_value

    with open(settings_file, "w") as f:
        json.dump(settings_dict, f, indent=4)
