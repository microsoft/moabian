# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import sys
from distutils.core import setup
from distutils.extension import Extension

if '--use-cython' in sys.argv:
    use_cython = True
    sys.argv.remove('--use-cython')
else:
    use_cython = False

# Force use_cython = False for moab v3.0 setup
# install with: 
# pip3 install .

ext = '.pyx' if use_cython else '.c'

extensions = [
    Extension(
        name="huemask",
        sources=["huemask"+ext],
        library_dirs=["/usr/local/lib"],
        include_dirs=["/usr/local/include"],
    )
]

if use_cython:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, compiler_directives={"language_level": 3})

version="3.0.0"

print(f"Installing {version}", flush=True)

setup(
    name="huemask",
    version=version,
    description="Python bindings for huemask",
    ext_modules=extensions,
    package_data={"huemask": ["huemask.pyi"]},
)

