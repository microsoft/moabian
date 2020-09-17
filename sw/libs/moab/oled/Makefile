# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

NAME=oled
OBJECTS=
CFLAGS=-Wall -O3 -std=gnu11
LDLIBS=-L/usr/local/lib
LDFLAGS=-lmoab -lbcm2835
CC=gcc

$(NAME): $(OBJECTS)

clean:
	$(RM) $(NAME)


PREFIX=/usr/local/bin

install: $(NAME)
	cp oled $(PREFIX)
