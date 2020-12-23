// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#ifndef SPI_H
#define SPI_H

#include <bcm2835.h>
#include <stdbool.h>
#include <stdint.h>

#define SEND_PACKET_BYTES 7
#define ICON_BITS 3
#define RECEIVE_PACKET_BYTES 7
#define MAXSIZE 1023

//  Defining receive SPI packet    //
typedef union
{
    struct
    {
        uint8_t menu: 1;
        uint8_t joystick: 1;
        uint8_t res: 6;
    };
    char raw;
} hat_buttons;

typedef union
{
    struct
    {
        hat_buttons buttons;
        int8_t joystick_x;
        int8_t joystick_y;
    };
    char combined_packet[RECEIVE_PACKET_BYTES];
}receive_packet_type;

//  Defining send SPI packet  //
typedef union
{
    struct
    {
        uint8_t servo_en: 1;
        uint8_t servo_control: 1;
        uint8_t ip_message: 1;
        uint8_t arbitrary: 1;
        uint8_t version_message: 1;
        uint8_t res: 3;
    };
    char raw;
} mssg_control;
typedef union
{
    struct
    {
        uint8_t icon: 3;
        uint8_t text: 5;
    };
    char raw;
} disp_control;
typedef union 
{
    struct 
    {
        uint8_t menu_item: 1;
        uint8_t scroll_text: 1;
        uint8_t res: 2;
        // Replacment text should be in the form of an integer defined in mode.h
        uint8_t text_to_replacement: 4;
    };
    char raw;  
} text_control;

// Standard Mssg
typedef union
{
    struct
    {
        mssg_control control;
        disp_control display;
        char plate_angle_x;
        char plate_angle_y;
        char servo1_pos;
        char servo2_pos;
        char servo3_pos;
    };
    char combined_packet[SEND_PACKET_BYTES];
} send_packet_standard;

// Info Message IP
typedef union
{
    struct
    {
        mssg_control control;
        char IP_1;
        char IP_2;
        char IP_3;
        char IP_4;
        char res1;
        char res2;
    };
    char combined_packet[SEND_PACKET_BYTES];
} send_packet_ip;

// Info Message Version
typedef union
{
    struct
    {
        mssg_control control;
        char sw_major;
        char sw_minor;
        char sw_bug;
        char res1;
        char res2;
        char res3;
    };
    char combined_packet[SEND_PACKET_BYTES];
} send_packet_version;

// Arbitrary text
typedef union
{
    struct
    {
        mssg_control control;
        text_control text_control;
        char string_length;
    };
    char combined_packet[MAXSIZE];
} send_packet_text;



/*--------------------------------------
|=	transceive()
|=	Sends & receives single byte over spi
--------------------------------------*/
char transceive(char data_out);

/*--------------------------------------
|=	transceive_packet()
|=	Sends & receives multiple bytes over spi
--------------------------------------*/
char *transceive_packet(char* data_out, char* data_in, int size);

#endif
