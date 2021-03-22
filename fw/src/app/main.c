// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "app_version.h"
#include "plate.h"
#include "spi.h"
#include "display.h"

LOG_MODULE_REGISTER(main);

void main(void)
{
    pi_to_hat_t rx;
    u8_t last_control;

    u8_t mb_idx = 0;
    char message_buffer[255];

    float servo1_pos, servo2_pos, servo3_pos;
    u16_t servo1_pos_centi_deg, servo2_pos_centi_deg, servo3_pos_centi_deg;

    LOG_INF("Version %s", log_strdup(APP_SEMVER));
    LOG_INF("Word Size %d. pi_to_hat_t %d", sizeof(void *), sizeof(pi_to_hat_t));

    plate_init();

    while (true)
    {
        // process incoming SPI msgs
        if (wait_for_pi_message(&rx, K_FOREVER) == 0)
        {
            last_control = rx.control;

            switch (rx.control)
            {
                case COPY_STRING:
                    if (mb_idx == 0)
                        memset(message_buffer, 0, sizeof(message_buffer));
                    if (mb_idx < 240) {
                        memcpy(&message_buffer[mb_idx], rx.data.characters, 7);
                        mb_idx += 7;
                    }
                    else
                        LOG_ERR("String is too long to display. Max length is 240 bytes.");
                    break;

                case DISPLAY_BIG_TEXT_ICON:
                    message_buffer[mb_idx] = '\0';  // Add a termination char just in case
                    mb_idx = 0;
                    LOG_INF("icon(%d) TEXT=%s", (u8_t) rx.data.icon, log_strdup(message_buffer));
                    display_big_text_icon(message_buffer, (disp_icon_t) rx.data.icon);
                    break;

                case DISPLAY_BIG_TEXT:
                    message_buffer[mb_idx] = '\0';  // Add a termination char just in case
                    mb_idx = 0;
                    LOG_INF("TEXT=%s", log_strdup(message_buffer));
                    display_big_text(message_buffer);
                    break;

                case DISPLAY_SMALL_TEXT:
                    message_buffer[mb_idx] = '\0';  // Add a termination char just in case
                    mb_idx = 0;
                    LOG_INF("text=%s", log_strdup(message_buffer));
                    display_small_text(message_buffer);
                    break;

                case DISPLAY_POWER_SYMBOL:
                    message_buffer[mb_idx] = '\0';  // Add a termination char just in case
                    mb_idx = 0;
                    LOG_INF("power(%d) TEXT=%s", (u8_t) rx.data.icon, log_strdup(message_buffer));
                    display_big_text_power_icon(message_buffer, (disp_power_icon_t) rx.data.icon);
                    break;

                case SERVO_ENABLE:
                    LOG_INF("servos: on");
                    plate_servo_enable(true);
                    break;

                case SERVO_DISABLE: 
                    LOG_INF("servos: off");
                    plate_servo_enable(false);
                    break;

                case SET_SERVOS:
                    // Convert bytes to uint16
                    servo1_pos_centi_deg = ((rx.data.servo1_pos_centi_deg_high_byte << 8) + rx.data.servo1_pos_centi_deg_low_byte);
                    servo2_pos_centi_deg = ((rx.data.servo2_pos_centi_deg_high_byte << 8) + rx.data.servo2_pos_centi_deg_low_byte);
                    servo3_pos_centi_deg = ((rx.data.servo3_pos_centi_deg_high_byte << 8) + rx.data.servo3_pos_centi_deg_low_byte);
                    // Convert from hundredths of a degree to degrees
                    servo1_pos = ((float) servo1_pos_centi_deg) / 100.0;
                    servo2_pos = ((float) servo2_pos_centi_deg) / 100.0;
                    servo3_pos = ((float) servo3_pos_centi_deg) / 100.0;

                    plate_servo_update_position(0, servo1_pos);
                    plate_servo_update_position(1, servo2_pos);
                    plate_servo_update_position(2, servo3_pos);
                    break;

                case NOOP:
                    break;

                default:
                    LOG_ERR("Bad control byte: %x. Prior was: %x", rx.control, last_control);
                    break;
            }
        }
    }
}
