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

void spi_task(void)
{
	struct device *spi;
	struct spi_config       spi_cfg;
	struct spi_cs_control   spi_cs;

	spi = device_get_binding("SPI_1");
	if (!spi)
	{
		LOG_ERR("Could not find SPI driver\n");
		return;
	}

	spi_cfg.operation = SPI_WORD_SET(8) | SPI_OP_MODE_SLAVE;
	spi_cfg.frequency = 25000000;

	spi_cs.gpio_dev = device_get_binding(DT_INST_0_ST_STM32_SPI_CS_GPIOS_CONTROLLER);
	spi_cs.gpio_pin = DT_INST_0_ST_STM32_SPI_CS_GPIOS_PIN;
	spi_cs.delay = 0;
	spi_cfg.cs = &spi_cs;

	LOG_INF("SPI interface listening");

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

	while(true)
	{
        // prevent CS from being treated as an output after SPI operation.
		// TODO: find a proper solution to keep CS as an input pin
		gpio_pin_configure(spi_cs.gpio_dev, DT_INST_0_ST_STM32_SPI_CS_GPIOS_PIN, GPIO_DIR_IN);
		
		memset(&pi_to_hat, 0, sizeof(pi_to_hat));       // 8 bytes from Raspberry Pi (Tx)
        memset(&hat_to_pi, 0, sizeof(hat_to_pi));       // 8 bytes to   Raspberry Pi (Rx)

        hat_to_pi.menu_button = atomic_get(&g_btn_menu);
        hat_to_pi.joystick_button = atomic_get(&g_btn_joy);
        hat_to_pi.joystick_x = (int) atomic_get(&g_joy_x);
        hat_to_pi.joystick_y = (int) atomic_get(&g_joy_y);

        // tx: outbound (button state and joystick positions)
        // rx: incoming (command verbs)

		if (spi_transceive(spi, &spi_cfg, &tx, &rx) > 0)
		{
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
