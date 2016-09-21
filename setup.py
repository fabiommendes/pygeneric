# -*- coding: utf-8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/python-boilerplate/
#

import os
import sys
from setuptools import setup, find_packages

# Save version and author to __meta__.py
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'src', 'generic', '__meta__.py')
meta = '''# Automatically created. Please do not edit.
__version__ = u'%s'
__author__ = u'F\\xe1bio Mac\\xeado Mendes'
''' % version
with open(path, 'w') as F:
    F.write(meta)

# Choose the default Python3 branch or the code converted by 3to2
PYSRC = 'src' if sys.version_info[0] == 3 else 'py2src'

# Cython stuff
setup_kwargs = {'cmdclass': {}}
if 'PyPy' not in sys.version:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
    except ImportError:
        import warnings

        warnings.warn(
            'Please install Cython to compile faster versions of pygeneric')
    else:
        try:
            setup_kwargs.update(ext_modules=cythonize('src/generic/*.pyx'))
            setup_kwargs['cmdclass']['build_ext'] = build_ext
        except ValueError:
            pass

# Bellow Python 3.5, we have a dependency on the typing module
if sys.version_info < (3, 5):
    typing_dep = ['typing']
else:
    typing_dep = []
    

setup(
    # Basic info
    name='pygeneric',
    version=version,
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='http://github.com/fabiommendes/pygeneric/',
    description='A short description for your project.',
    long_description=open('README.rst').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'six'
    ] + typing_dep,
    extras_require={
        'dev': [
            'psutil',
            'pexpect',
            'python-boilerplate',
            'invoke>=0.13',
            'pytest',
        ],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
    **setup_kwargs
)
