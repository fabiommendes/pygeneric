# -*- coding: utf8 -*-
#
# This is my "best-practices" project structure that I copy and past to other
# projects. Fell free to imitate. It is mostly based on advice from
#
#   https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project
# -the-right-way/
#
# but with a few twists.
#
import os
import sys
import setuptools
from setuptools import setup


AUTHOR = 'Fábio Macêdo Mendes'
BASE, _ = os.path.split(__file__)
SRC = os.path.join(BASE, 'src')
setup_kwds = dict(cmdclass={})


#
# Update VERSION and meta.py with meta information
#
with open(os.path.join(BASE, 'VERSION')) as F:
    VERSION = F.read().strip()

with open(os.path.join(SRC, 'generic', 'meta.py'), 'w') as F:
    F.write(
        '# Auto-generated file. Please do not edit\n'
        '__version__ = %r\n' % VERSION +
        '__author__ = %r\n' % AUTHOR)


#
# Choose the default Python3 branch or the code converted by 3to2
#
PYSRC = 'src' if sys.version_info[0] == 3 else 'py2src'

#
# Test integration
#
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)
setup_kwds['cmdclass']['test'] = PyTest

#
# Cython stuff
#
if 'PyPy' not in sys.version:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
    except ImportError:
        import warnings
        warnings.warn('Please install Cython to compile faster versions of FGAme modules')
    else:
        try:
            setup_kwds.update(ext_modules=cythonize('src/generic/*.pyx'))
            setup_kwds['cmdclass']['build_ext'] = build_ext
        except ValueError:
            pass

#
# Main configuration script
#
setup(
    name='pygeneric',
    version=VERSION,
    description='Generic functions for Python',
    author=AUTHOR,
    author_email='fabiomacedomendes@gmail.com',
    url='https://github.com/fabiommendes/pygeneric',
    long_description="""
`pygeneric` implements generic functions with type dispatch in Python. A generic
function groups different implementations (or methods) under the same name.
The actual implementation is then chosen at runtime depending on the function
arguments.

The implementation is loosely inspired in the Julia language. We also shamelessly
steal some other features of Julia and adapted them to Python:
    * Parametric types.
    * A type conversion/promotion system integrated with arithmetic operations.
    * A generic Object base class that delegates all binary operations to the
      corresponding generic functions (i.e., instead of implementing
      Object.__add__, we overload add(Object, Object)).

This package works with Python 3 and Python 2, but it is getting increasingly
more difficult to keep Python 2 support as we implement more advanced features.
We would love to let it go of Python 2, so please tell us if you use this package
in Python 2.
""",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    package_dir={'': PYSRC},
    packages=setuptools.find_packages(PYSRC),
    license='GPL',
    install_requires=['six'],
    zip_safe=False,
    tests_require=['pytest', 'psutil', 'manuel'],
    setup_requires=[],
    **setup_kwds
)
