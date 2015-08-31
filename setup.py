#-*- coding: utf8 -*-
import os
import setuptools
from setuptools import setup

VERSION = '0.1a1'
AUTHOR = 'Fábio Macêdo Mendes'
setup_kwds = {}

#
# Create meta.py file with updated version/author info
#
base, _ = os.path.split(__file__)
path = os.path.join(base, 'src', 'generic', 'meta.py')
with open(path, 'w') as F:
    F.write(
        '# Auto-generated file. Please do not edit'
        '__version__ = %r\n' % VERSION +
        '__author__ = %r\n' % AUTHOR)


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
    long_description=(
        r'''``pygeneric`` makes it easy to create generic functions in Python,
i.e., functions whose implementation is different depending on the input
argument types.'''),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Operating System :: WINDOWS',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    license='GPL',
    requires=['six'],
)
