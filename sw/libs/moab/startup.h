// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#ifndef STARTUP_H
#define STARTUP_H

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <bcm2835.h>
// Functions for getting IP Address //
#include <errno.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BOOT_EN   RPI_BPLUS_GPIO_J8_29
#define FAN_EN    RPI_BPLUS_GPIO_J8_37
#define HAT_EN    RPI_BPLUS_GPIO_J8_38
#define HAT_RESET RPI_BPLUS_GPIO_J8_31
#define HAT_PWR_N RPI_BPLUS_GPIO_J8_05

#define PIN_READ(pin) (bcm2835_gpio_lev(pin))
#define SET_HIGH(pin) (bcm2835_gpio_set(pin))
#define SET_LOW(pin)  (bcm2835_gpio_clr(pin))

typedef enum boot_mode{DEFAULT, BOOTLOADER}boot_mode;

/*--------------------------------------
|=	pi_init()
|=	initializes the what is needed for RPI
--------------------------------------*/
void pi_init(uint8_t mode_bootloader);
void runtime();
void gpio_init();
char* getEnvOrDefaultTo(char* env, char* defaultVal);
#endif
