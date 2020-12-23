# https://gist.github.com/ctokheim/6c34dc1d672afca0676a

.PHONY: build install uninstall clean cython all

all: clean build-cython install clean

build: clean
	python3 setup.py build_ext --inplace

build-cython: clean
	@echo "BUILD-PYTHON"
	python3 setup.py build_ext --inplace --use-cython

clean:
	@echo "CLEAN"
	rm -f -r build/
	rm -f src/python/cython_utils.so
	rm -f *.so

moab.c: moab.pyx
	python3 setup.py build

install: 
	@echo "INSTALL"
	pip3 install .

uninstall:
	pip3 uninstall -y pymoab
