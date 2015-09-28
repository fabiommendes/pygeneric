#-*- coding: utf8 -*-
import os
import sys
import setuptools
from setuptools import setup

AUTHOR = 'Fábio Macêdo Mendes'
BASE, _ = os.path.split(__file__)
SRC = os.path.join(BASE, 'src')
setup_kwds = {}


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
# Cython stuff
#
try:
    if 'PyPy' not in sys.version:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
        setup_kwds.update(
            ext_modules=cythonize('src/generic/*.pyx'),
            cmdclass={'build_ext': build_ext})
except ImportError:
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
    long_description=open(os.path.join(BASE, 'README.txt')).read(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    license='GPL',
    install_requires=[
        'six',
    ],
    **setup_kwds
)
