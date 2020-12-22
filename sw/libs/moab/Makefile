# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

CFLAGS := -O3 -g -Wall -Werror
CC := gcc
MAJOR := 2
MINOR := 5
NAME := moab
VERSION := $(MAJOR).$(MINOR)
LDLIBS=-L/usr/local/lib
LDFLAGS=-lbcm2835
SHARED=-shared -Wl,-soname,lib$(NAME).so.$(MAJOR)
PREFIX=/usr/local/lib

lib: lib$(NAME).so

install: lib$(NAME).so.$(VERSION)
	cp moab.h /usr/local/include
	cp $^ $(PREFIX)
	ldconfig -v -n $(PREFIX)
	ln -f -s $(PREFIX)/lib$(NAME).so.$(MAJOR) $(PREFIX)/lib$(NAME).so
	ldconfig
	chmod 644 $(PREFIX)/lib$(NAME)*
	$(RM) *.o *.so*

lib$(NAME).so: lib$(NAME).so.$(VERSION)
	ldconfig -v -n .
	ln -s lib$(NAME).so.$(MAJOR) lib$(NAME).so

lib$(NAME).so.$(VERSION): $(NAME).o spi.o startup.o
	$(CC) $(LDLIBS) $(SHARED) $(LDFLAGS) $^ -o $@

clean:
	$(RM) *.o *.so*
