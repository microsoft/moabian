// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <bcm2835.h>
#include "../moab.h"

char *options = 
"ICON_BLANK 0\t"
"TXT_BLANK 0\n"

"ICON_UP_DOWN 1\t"
"TXT_INIT 1\n"

"ICON_DOWN 2\t"
"TXT_POWER_OFF 2\n"

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

int main(int argc, char* argv[]) { 

    int icon = 0;
    int text = 0;

    if (argc != 3) {
        printf("Usage: %s icon# text#\n", argv[0]);
        printf("*Must run as root*\n");
        printf("\nExamples:\n");
        printf("\n");
        printf("oled 4 10 \t# dot / BOT INFO\n");
        printf("oled 0  0 \t# clear oled screen\n");
        printf("oled 0  1 \t# INITIALIZING\n");
        printf("oled 0  2 \t# POWER OFF\n");
        printf("oled 0 18 \t# PROJECT MOAB\n");
        printf("\n");
        printf(options);
        return(1);
    }

    if (geteuid() != 0) {
        printf("Run this as root\n");
        return(1);
    }

    icon = atoi(argv[1]);
    text = atoi(argv[2]);

    moab_init();
    moab_setIcon(icon);
    moab_setText(text);
    moab_sync();

    bcm2835_spi_end();
    bcm2835_close();
}



