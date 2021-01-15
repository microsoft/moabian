# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

NAME=oled
OBJECTS=oled.o
CFLAGS=-Wall -O3
LDLIBS=-lbcm2835
CC=gcc

$(NAME): $(OBJECTS)

clean:
	$(RM) $(NAME)
	$(RM) $(OBJECTS)

PREFIX=/usr/local/bin

install: $(NAME)
	cp oled $(PREFIX)
