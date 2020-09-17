// vim: noai:ts=4:sw=4

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <bcm2835.h>
#include <unistd.h>

#define BOOT_EN   RPI_BPLUS_GPIO_J8_29
#define FAN_EN    RPI_BPLUS_GPIO_J8_37
#define HAT_EN    RPI_BPLUS_GPIO_J8_38
#define HAT_RESET RPI_BPLUS_GPIO_J8_31
#define HAT_PWR_N RPI_BPLUS_GPIO_J8_05


#define PIN_READ(pin) (bcm2835_gpio_lev(pin))
#define SET_HIGH(pin) (bcm2835_gpio_set(pin))
#define SET_LOW(pin)  (bcm2835_gpio_clr(pin))

int bootloader(char* binary_name)
{
    // firmware upload command
    char command[256] = "mcumgr --conntype=serial --connstring=/dev/ttyAMA1,baud=115200 image upload ";
    int status;

    printf("Bootloader mode\n");
    SET_HIGH(HAT_EN);
    SET_HIGH(BOOT_EN);
    SET_HIGH(HAT_RESET);
    delay(250);
    SET_LOW(HAT_RESET);

    strcat(command, binary_name);
    printf("Running: %s\n", command);

    status = system(command);

    SET_LOW(BOOT_EN);
    SET_HIGH(HAT_RESET);
    delay(250);
    SET_LOW(HAT_RESET);

    return status;
}


int gpio_init()
{
    if (!bcm2835_init()) return(0);
    if (!bcm2835_spi_begin()) return(0);

    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);      // The default
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);                   // The default
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_65536); // The default
    bcm2835_spi_chipSelect(BCM2835_SPI_CS0);                      // The default
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // The default

    bcm2835_gpio_fsel(BOOT_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_RESET, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(FAN_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_PWR_N, BCM2835_GPIO_FSEL_INPT);
    return(1);
}


int main(int argc, char *argv[])
{
    int opt;

    // Requires one argument (the .bin filename)
    if (argc != 2) {
        printf("Usage: hatflash firmware.bin\n");
        return (-1);
    }
    char* path = argv[1];

    if (!gpio_init())
	{
		printf("bcm2835 initialize failed. Are you running as root?\n");
		return(-1);
	}

	int status = bootloader(path);
    if (status != 0)
	{
		printf("Firmware installed failed: %d\n", status);	
	}
    return(0);
}

