// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "startup.h"

/*--------------------------------------
|=  Function: software_and_IP_to_config
|= ------------------------------------
|=  Gets environment variable or returns default value specified
|=
|=	Returns: char*
--------------------------------------*/
char* getEnvOrDefaultTo(char* env, char* defaultVal)
{
    char* result = getenv(env);
    return result == NULL ? defaultVal: result;
}

/*--------------------------------------
|=	Function: runtime
|=	------------------------------------
|=	Turns the hat on in normal operation mode
|=
|=	Returns: Void
--------------------------------------*/
void runtime()
{
	SET_LOW(HAT_EN);
	delay(20);
	SET_HIGH(HAT_EN);
	SET_LOW(HAT_RESET);
	SET_LOW(BOOT_EN);
    delay(250);
}

/*--------------------------------------
|=	Function: BCM_spi_init
|=	------------------------------------
|=	Enables the BCM2835 SPI bus
|=
|=	Returns: Void
--------------------------------------*/
static void BCM_spi_init(){
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);      // The default
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);                   // The default
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_65536); // The default
    bcm2835_spi_chipSelect(BCM2835_SPI_CS0);                      // The default
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // The default
}

/*--------------------------------------
|=	Function: gpio_init
|=	------------------------------------
|=	Initializes the GPIO used by the BCM2835
|=
|=	Returns: 1 for passed || 0 for failed
--------------------------------------*/
void gpio_init(){

    if (!bcm2835_init())
    {
      printf("bcm2835_init failed. Are you running as root??\n");
      exit(1);
    }
    if (!bcm2835_spi_begin())
    {
      printf("bcm2835_spi_begin failed. Are you running as root??\n");
      exit(1);
    }
    BCM_spi_init();

    bcm2835_gpio_fsel(BOOT_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_RESET, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(FAN_EN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(HAT_PWR_N, BCM2835_GPIO_FSEL_INPT);
}

