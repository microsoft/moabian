# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from distutils.core import setup
from distutils.extension import Extension

extensions = [
    Extension(
        name="pymoab",
        sources=["moab.pyx"],
        libraries=["moab", "bcm2835"],
        library_dirs=["/usr/local/lib"],
        include_dirs=["/usr/local/include"],
    )
]


# if cython is installed, build from source, otherwise use moab.c
try:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, compiler_directives={"language_level": 3})
except ImportError:
    pass

setup(
    name="pymoab",
    version="1.0.0",
    description="Python bindings for libmoab",
    ext_modules=extensions,
    package_data={"pymoab": ["pymoab.pyi"]},
)
