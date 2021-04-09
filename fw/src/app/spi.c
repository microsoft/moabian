// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "headers.h"
#include "state.h"
#include "spi.h"
LOG_MODULE_REGISTER(spi);

#define STACKSIZE 1024
#define PRIORITY 2

static pi_to_hat_t  pi_to_hat;
static hat_to_pi_t  hat_to_pi;

typedef struct fifo_item_t {
    void *fifo_reserved; /* 1st word reserved for use by fifo */
    pi_to_hat_t msg;
} fifo_item_t;

fifo_item_t fifo_rx_queue;

K_FIFO_DEFINE(my_fifo);

// Read message received from the pi out of the FIFO
// Call not thread safe. Run from one thread at a time.
// Returned message buffer must be freed after processing is done.
int wait_for_pi_message(pi_to_hat_t* msg, int32_t timeout)
{
    fifo_item_t *rx_data = k_fifo_get(&my_fifo, timeout);
    if (rx_data == NULL)
        return -1;

    // shallow copy ok?
    *msg = rx_data->msg;
    k_free(rx_data);
    return 0;
}

// Zephyr thread to read and write data over the
// SPI bus to/from the pi.
void spi_task(void) 
{
    struct device *spi;
    struct spi_config       spi_cfg;
    struct spi_cs_control   spi_cs;
    int spi_trancieve_ret = 0;

    // Get SPI device binding from Zephyr device tree
    spi = device_get_binding("SPI_1");
    if (!spi)
    {
    	LOG_ERR("Could not find SPI driver\n");
    	return;
    }

    // Set-up config struct for SPI
    // Note: using custom patch for Zephyr 2.1 SPI driver to correct operation
    // in slave mode. OS upgrades will need the patch implemented in spi_ll_stm32.c
    // and spi_context.h. spi_cfg.cs must be set for patch to work correctly.
    spi_cfg.operation = SPI_WORD_SET(8) | SPI_OP_MODE_SLAVE;
    spi_cfg.frequency = 25000000;

    spi_cs.gpio_dev = device_get_binding(DT_INST_0_ST_STM32_SPI_CS_GPIOS_CONTROLLER);
    spi_cs.gpio_pin = DT_INST_0_ST_STM32_SPI_CS_GPIOS_PIN;
    spi_cs.delay = 0;
    spi_cfg.cs = &spi_cs;

    LOG_INF("SPI interface listening");

    // Init Rx and Tx buffers
    const struct spi_buf tx_buf = {
        .buf = &hat_to_pi,
        .len = sizeof(hat_to_pi)
    };
    const struct spi_buf rx_buf =
    {
        .buf = &pi_to_hat,
        .len = sizeof(pi_to_hat)
    };
    const struct spi_buf_set tx = { .buffers = &tx_buf, .count = 1 };
    const struct spi_buf_set rx = { .buffers = &rx_buf, .count = 1 };

    // Infinite loop in dedicated thread to transfer data over SPI bus
    while(true)
    {
        // Fill Tx buff with message for PI
        memset(&pi_to_hat, 0, sizeof(pi_to_hat));       // 8 bytes from Raspberry Pi (Tx)
        memset(&hat_to_pi, 0, sizeof(hat_to_pi));       // 8 bytes to   Raspberry Pi (Rx)

        hat_to_pi.menu_button = atomic_get(&g_btn_menu);
        hat_to_pi.joystick_button = atomic_get(&g_btn_joy);
        hat_to_pi.joystick_x = (int) atomic_get(&g_joy_x);
        hat_to_pi.joystick_y = (int) atomic_get(&g_joy_y);

        // tx: outbound (button state and joystick positions)
        // rx: incoming (command verbs)

        // Send and recieve data from the Pi. No limit on wait length.
        spi_trancieve_ret = spi_transceive(spi, &spi_cfg, &tx, &rx);

        // Process transfer results
        if(spi_trancieve_ret != sizeof(pi_to_hat))
        {
            // did not recieve full length packet or an error was encountered
            // in the SPI driver during the transfer

            if(spi_trancieve_ret >= 0) // was the data the wrong length?
                LOG_INF("Recieved %d bytes from pi but expected %d.", spi_trancieve_ret, sizeof(pi_to_hat));
            else // Internal SPI driver error
                LOG_ERR("Pi-Hat spi_transceive() returned with error: %d", spi_trancieve_ret);
        }
        else
        {
            // Valid packet was recieved. Put on FIFO queue for later processing.
            size_t size = sizeof(fifo_item_t);
            fifo_item_t *ptr = (fifo_item_t *) k_malloc(size);
            __ASSERT_NO_MSG(ptr != 0);

            ptr->fifo_reserved = 0x0;           // don't care
            memcpy(&ptr->msg, &pi_to_hat, sizeof(pi_to_hat));

            k_fifo_put(&my_fifo, ptr);
        }
    }
}

K_THREAD_DEFINE(spi_task_id, STACKSIZE, spi_task, NULL, NULL, NULL, PRIORITY, 0, K_NO_WAIT);
