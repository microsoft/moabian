# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from hat import Hat, Icon, PowerIcon

with Hat() as hat:

    hat.display_power_symbol("GOODBYE", PowerIcon.SLEEP_MODE)
