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

ext = '.pyx' if use_cython else '.c'


extensions = [
    Extension(
        name="pymoab",
        sources=["moab"+ext],
        libraries=["moab", "bcm2835"],
        library_dirs=["/usr/local/lib"],
        include_dirs=["/usr/local/include"],
    )
]

# extensions = [
#     Extension(
#         name="pymoab",
#         sources=["moab.pyx"],
#         libraries=["moab", "bcm2835"],
#         library_dirs=["/usr/local/lib"],
#         include_dirs=["/usr/local/include"],
#     )
# ]

if use_cython:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, compiler_directives={"language_level": 3})

version=os.environ.get("MOABIAN", "1.0.0")

print(f"Installing {version}")

setup(
    name="pymoab",
    version=version,
    description="Python bindings for libmoab",
    ext_modules=extensions,
)
    #package_data={"pymoab": ["pymoab.pyi"]},

