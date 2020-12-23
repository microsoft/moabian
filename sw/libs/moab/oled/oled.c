// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <bcm2835.h>
#include <string.h>         // memset
#include "spi.h"

#ifdef USE_MOABLIB
#include "../moab.h"
#endif

static char* get_options();
void spi_setup();
void send_icon_text(int icon, int text);
void print_bytes(char* header, const void *object, size_t size);

int main(int argc, char* argv[]) { 

    int icon = 0;
    int text = 0;

    if (argc != 3) {
        printf("Usage: %s icon# text#\n\n", argv[0]);
        printf("Must run as root\n");
        printf("\nExamples:\n");
        printf("\n");
        printf("oled 4 10 \t# dot / BOT INFO\n");
        printf("oled 0  0 \t# clear oled screen\n");
        printf("oled 0  1 \t# INITIALIZING\n");
        printf("oled 0  2 \t# POWER OFF\n");
        printf("oled 0 18 \t# PROJECT MOAB\n");
        printf("\n");
        printf(get_options());
        return(1);
    }

    if (geteuid() != 0) {
        printf("Run this as root\n");
        return(1);
    }

    icon = atoi(argv[1]);
    text = atoi(argv[2]);

#ifdef USE_MOABLIB
    moab_init();
    moab_setIcon(icon);
    moab_setText(text);
    moab_sync();
#else
    spi_setup();
    send_icon_text(icon, text);
#endif

    bcm2835_spi_end();
    bcm2835_close();
}

void send_icon_text(int icon, int text)
{
    send_packet_standard tx;
    receive_packet_type rx;

    memset(&tx, 0, sizeof tx);
    memset(&rx, 0, sizeof rx);

    tx.display.icon = icon;        //# 3 bits
    tx.display.text = text;        //# 5 bits

    print_bytes("tx:", tx.combined_packet, sizeof tx);

    bcm2835_spi_transfernb(tx.combined_packet, rx.combined_packet, SEND_PACKET_BYTES);

    print_bytes("rx:", rx.combined_packet, sizeof rx);
}

void print_bytes(char* header, const void *object, size_t size)
{
    const unsigned char * const bytes = object;

    printf("%s\n", header);
    printf("[ ");
    for(size_t i = 0; i < size; i++) {
        printf("%02x ", bytes[i]);
    }
    printf("]\n");
}



static char* get_options()
{
    static char *options = 
    "TXT_BLANK 0\t"
    "ICON_BLANK 0\n"

    "TXT_INIT 1\t"
    "ICON_UP_DOWN 1\n"

    "TXT_POWER_OFF 2\t"
    "ICON_DOWN 2\n"

    "TXT_ERROR 3\t"
    "ICON_UP 3\n"

    "TXT_CAL 4\t"
    "ICON_DOT 4\n"

    "TXT_MANUAL 5\t"
    "ICON_PAUSE 5\n"

    "TXT_CLASSIC 6\t"
    "ICON_CHECK 6\n"

    "TXT_BRAIN 7\t"
    "ICON_X 7\n"

    "TXT_CUSTOM1 8\n"
    "TXT_CUSTOM2 9\n"
    "TXT_INFO 10\n"
    "TXT_CAL_INSTR 11\n"
    "TXT_CAL_COMPLETE 12\n"
    "TXT_CAL_CANCELED 13\n"
    "TXT_CAL_FAILED 14\n"
    "TXT_VERS_IP_SN 15\n"
    "TXT_UPDATE_BRAIN 16\n"
    "TXT_UPDATE_SYSTEM 17\n"
    "TXT_PROJECT_MOAB 18\n";
    return options;
}


void spi_setup()
{
    if (!bcm2835_init()) {
        printf("bcm2835_init failed\n");
        exit(1);
    }

    if (!bcm2835_spi_begin()) {
        printf("bcm2835_spi_begin failed\n");
        exit(1);
    }
}

