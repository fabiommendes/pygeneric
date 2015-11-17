============
Installation
============


Dependencies
============

`pygeneric` can run in many Python implementations including CPython and 
PyPy. In CPython it can be installed as a (slower) pure-python version or it
can use a Cython compiled extensions to speed-up things in C.

Don't be alarmed if you are running an unoptimized code: these speed benefits
are negligible unless you are dispatching to very simple functions that are
called many times in tight loops.


Installation commands
=====================

If you downloaded the pygeneric compressed package, simply unpack it and 
execute the regular Python install::

    $ python setup.py build
    $ sudo python setup.py install

`pygeneric` is also available at PyPI and hence can be installed using `pip`::

    $ sudo pip install pygeneric
    
In Windows the command would be something like this (adapt for the correct 
Python installation path)::

    $ cd c:\python34
    $ python -m pip install pygeneric
