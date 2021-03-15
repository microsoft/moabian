from hat import Hat, Icon, PowerIcon

with Hat() as hat:
    hat.display_string_icon("DOT", Icon.DOT)
    input("Confirm: • DOT")

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
        0: "Berkeley\nCalifornia",
        1: "Sacramento\nVacaville\nBerkeley\nSan Luis Obispo",
        2: "Sacramento Vacaville\nKansas City\nBerkeley San Luis Obispo CA",
    }

    hat.display_long_string(menus[0])
    input("Confirm: 2 lines, not scrolling")

    hat.display_long_string(menus[1])
    input("Confirm: 4 lines, vertical scroll")

    hat.display_long_string(menus[2])
    input("Confirm: 2 lines, horizontal scroll")
