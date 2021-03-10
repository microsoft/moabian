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

