# https://gist.github.com/ctokheim/6c34dc1d672afca0676a

clean:
	rm -f -r build/
	rm -f src/python/cython_utils.so

clean-cpp:
	rm -f src/python/cython_utils.cpp

clean-all: clean clean-cpp

moab.c: moab.pyx
	python3 setup.py build

.PHONY: install
install: 
	pip3 install .

uninstall:
	pip3 uninstall -y pymoab


.PHONY: build
build: clean
	python setup.py build_ext --inplace

.PHONY: cython-build
cython-build: clean clean-cpp
	python setup.py build_ext --inplace --use-cython

