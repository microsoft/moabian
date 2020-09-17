# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os

# Both config.json and calibration.json live under "config/" relative to main.py.
# This way, one can edit the host's config/calibration.json, then launch the container
# overriding the container's version.

config_path = os.path.abspath(f"{os.getcwd()}/config/config.json")
moab_path = os.path.abspath(f"{os.getcwd()}/config")
calibration_path = f"{moab_path}/calibration.json"
