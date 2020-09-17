// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "spi.h"

/*--------------------------------------
|=	Function: transeive
|=	------------------------------------
|=	Sends and receives single packet to and from the SPI bus
|= 	
|=	data_out: data send to SPI bus
|=	Returns: data read from buffer
--------------------------------------*/
char transceive(char data_out){
	char data_in = bcm2835_spi_transfer(data_out);
	return data_in;
}

/*--------------------------------------
|=	Function: transeive_packet
|=	------------------------------------
|=	Sends and receives a packet of set length 
|=		to and from the SPI bus
|= 	
|=	*data_out: data send to SPI bus
|=	*data_in: data received from SPI bus
|=	size: # of bytes to read/write from SPI
|=	Returns: data read from buffer
--------------------------------------*/
char *transceive_packet(char *data_out, char *data_in, int size){
	bcm2835_spi_transfernb(data_out, data_in, size);
	return data_in;
}
