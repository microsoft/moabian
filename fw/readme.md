## Upgrading Moab Firmware

> Note: this is for the Moab power distribution "hat"
> The Raspberry Pi 4 takes care of upgrading it's EEPROM firmware.

```
sudo ./install.sh [fw-version.bin]
```

## Advanced

The firmware has an interactive shell where you can test the joystick,
activate the plate and read the OTP calibration banks.

For advanced use only. Interact with the firmware by making a connection
to over the serial port as shown below.

```bash
sudo minicom --device /dev/ttyAMA1 # (interactive shell)
```

* Press "enter" or "tab" to get to the `uart>` prompt.
* Exit with: ctrl-A Q

Log monitoring with:

```bash
sudo minicom --device /dev/ttyAMA0 # (log)
```

Troubleshooting firmware monitoring. Rpi4 might mask these external lines:

> /boot/cmdline.txt
remove the two console= lines

> /boot/config.txt
comment out dtoverlay=uart0


To check camera capabilities:

```bash
v4l2-ctl -d /dev/video0 --all

```

