# https://gist.github.com/ctokheim/6c34dc1d672afca0676a

.PHONY: install

all: huemask.c

huemask.c: huemask.pyx
	cython -3 huemask.pyx

install:
	@pip3 install .
