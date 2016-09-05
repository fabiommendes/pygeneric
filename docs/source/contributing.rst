=========================
Contributing to Pygeneric
=========================

This document explain how pygeneric is structured and its coding style. New
contributions are always welcome, but they must follow some rules to be
accepted.

If you like the workflow and want to adopt it in your project, please few
free to copy any part of the documentation and adapt it to your needs. The
documentation and all non-coding parts of the project are released under
creative commons. The source code itself is released under a Python ??? licence
(see LICENCE.txt) unless otherwise noted.


Non-coding contributions
========================

You can contribute to this project in many ways without having to write code.


Documentation
-------------

You can always improve documentation! Even small patches such as correcting
English mistakes and adding examples are valuable. The documentation is written in
`reSTructuredText`__ using `Sphinx`__, and is scattered among a few *.rst*
files and doc-strings in Python source.

You may find useful to have a reST cheat-sheet around, or the more maybe to have
a link to the more comprehensive `reference`__ handy for all those obscure
corner cases markup. We make a moderate use of Sphinx's
autodoc facilities, mainly to gather docstrings from Python functions and
classes. Most modules and higher level documentation should reside in the *.rst*
files under the project's */doc/source/* folder.

Docstrings uses `numpydoc`__ format (which requires an extra sphinx plugin). If
you are lazy to read all the manual, try to follow the template bellow:

.. ignore-next-block
.. code-block::python

    def add(x, y):
        """
        Short description (e.g.: Add two numbers).

        Long description paragraph. This optional paragraph tells more in-depth
        explanation of how the function behaves and of some of its properties.

        Parameters
        ----------

        x : number
            Description for the first parameter
        y : number
            Description for the first parameter

        Returns
        -------

        float:
            The sum of the two arguments.
            (your description for the function output)

        Raises
        ------

        You can document the possible failure modes for the function. Avoid
        specifying trivial errors such as TypeErrors for wrong parameters, but
        describe the conditions relevant to this function.

        See also
        --------

        sub: subtracts two numbers
        mul: multiply two numbers
        (other related functions)

        Examples
        --------

        Some example of the function's usage. Keep in mind that these examples
        are merely informative and should not be organized as unit tests! They
        describe how the function should be used in typical cases. We run all
        doctests and python code snippets in the documentation to certify that
        the documentation is correct, but don't count it as real coverage.

        To add two numbers, simply call :func:`add` on them!

        >>> add(1, 2)
        3

        This implementation respects the fact that zero is a neutral element of
        additions.

        >>> add(42, 0)
        42
        """

        return x + y


__ http://docutils.sourceforge.net/rst.html
__ http://www.sphinx-doc.org
__ https://pypi.python.org/pypi/numpydoc


Hey! I wanna code!
==================

Python 3
--------

All development is done in Python 3 and conversion to Python 2 is done before
deployment using the 3to2 tool. Humans should never touch Python 2
code! Check the pavement file for options passed to 3to2 during conversion.
We put no limit on the list of conversions, but this number should probably be
kept at a minimum for the sake of speed during the builds. Processing all rules
for all files can be expensive. Also, 3to2 sometimes introduces bugs, so we must
always keep the test suite alive in Python 2. We have no plans to support
Python <= 2.6: 2.7 support is a hassle as it is.


Chores
------

This project uses Invoke, which is a Pythonic version of Make/Rake/etc, to
administer many common chores in development. Installation, runtime and even
casual development should never depend on Invoke. However, the Invoke script
automates many chores and can make you daily development more productive. We build a
small library of functions under `chipsdev` which is a dependency for many Invoke
rules. ``pip install`` both of them if you want to be a regular contributor.

Once you have installed `chipsdev` and `invoke`, you can run the command
``invoke preparedev`` in order to install all development dependencies. It is
impossible to guarantee that it will work automatically for all platforms, but
unless your are using a common distribution (and not in Windows :-P) it should
work. I don't know anything about Python development in Windows. Tips and best
practices from Windows developers are welcome in this section!

__ http://docs.pyinvoke.org/


Style
-----

Always use `PEP8`__. `autopep8`__ and `pep8`__ are your friends to check if the
codebase adheres to the desired style. These rules are not sacred, but they
should not be violated gratuitously. We have a Paver rule for this.

__ http://pep8
__ http://autopep8..
__ http://pep8..

In order to


Testing
-------

This project uses `py.test`__ as the testing framework. It is a blow of a pythonic
fresh air when compared with the more traditional JUnit-style architecture of
:mod:`unittest`. We use a few extra plugins that are automatically installed
by setuptols before running ``$ python setup.py tests``. This includes a coverage
plugin for *pytest* and the `Manuel`__ package for checking if the examples in
the documentation are correct.

Ideally we should keep the test coverage above 90% at all times. Patches will
only be accepted if they came with the corresponding tests with 90%-ish coverage,
and at least a minimum working documentation.

__ http://pytest.org
__ https://pythonhosted.org/manuel/


Git flow
--------




Continuous integration
----------------------

We use the Travis-CI service for continuous integration.


