import sys
sys.path.append("/home/pi/moab/sw")

from hat import Hat, Icon, PowerIcon

with Hat() as hat:
    hat.display_string_icon("DOT", Icon.DOT)
    input("Confirm: • DOT")

    hat.display_string_icon("X Mark", Icon.X)
    input("Confirm: × Mark")

    hat.display_power_symbol("POWER", PowerIcon.POWER)
    input("Confirm: ⏻ POWER")

    hat.display_power_symbol("TOGGLE", PowerIcon.TOGGLE_POWER)
    input("Confirm: ⏼ TOGGLE")

    hat.display_power_symbol("ON", PowerIcon.POWER_ON)
    input("Confirm: ⏽ ON")

    hat.display_power_symbol("OFF", PowerIcon.POWER_OFF)
    input("Confirm: ⭘ OFF")

    hat.display_power_symbol("SLEEP", PowerIcon.SLEEP_MODE)
    input("Confirm: ⏾ SLEEP")

    menus = {
        0: "§ Berkeley\nCalifornia",
        1: "Albany\nKansas City\nBerkeley",
        2: "Vancouver, Canada...Albany, NY\nKansas City, MO...Berkeley, CA",
    }

    hat.display_long_string(menus[0])
    input("Confirm: 2 lines, not scrolling")

    hat.display_long_string(menus[1])
    input("Confirm: 4 lines, vertical scroll")

    hat.display_long_string(menus[2])
    input("Confirm: 2 lines, horizontal scroll")
