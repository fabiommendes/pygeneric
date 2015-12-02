============
Installation
============


Dependencies
============

`pygeneric` can run in many Python implementations including CPython and 
PyPy. In CPython, it can user a Cython compiled extension to speed-up things in
C. The effect is not dramatic unless you are calling very simple functions in
tight loops. The default pure-python implementation is fast enough for most
applications.

The only required dependency is the *six* package, which is very common and has
a good change to be already installed.


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

In any of these cases, it will fetch the required dependency on *six* if
necessary.