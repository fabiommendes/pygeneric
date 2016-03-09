"""
# Configuration options for the tasks.py script


[py2src]
fixes =
    newstyle
    kwargs
    division
    metaclass
    unpacking
    super
    annotations
encoding = utf-8
"""
from invoke import task, run
import configparser
parser = configparser.ConfigParser()
config = parser.read_string(__doc__)


#
# Transformations
#
@task
def py2src():
    """
    update the Python 2 source tree at py2src.
    """

    # Get all fixes
    fixes = config['py2src', 'fixes']
    if isinstance(fixes, str):
        if ',' in fixes:
            fixes = [x.strip(', ') for x in fixes.split(',')]
        else:
            fixes = fixes.split()
    else:
        fixes = list(fixes)
    fixes = ' '.join('-f %s' % fix for fix in fixes)

    # Move source to py2src folder and patch encoding
    run('cp src/ py2src/ -R')
    run('3to2 py2src/ --no-diffs -j4 -w %s' % fixes)


@task
def autopep8():
    """apply autopep8"""



#
# Deploy
#
def version_bump():
    """bumps the minor version number in the VERSION file"""


@task
def localdeploy():
    """install application with all dependencies in the local machine."""


@task
def virtualdeploy(path='virtualenv', fresh=False):
    """install application with all dependencies in the given virtualenv."""


@task
def dockerdeploy(path='virtualenv', fresh=False):
    """install application with all dependencies in the given docker."""


@task
def vmdeploy(path='virtualenv', fresh=False):
    """install application with all dependencies in the given virtual machine."""


#
# Distribution tasks
#
@task
def publish():
    """publish your project in PyPI and readthedocs.org.

    First it must have been registered with python setup.py register."""

@task
def publish_pypi():
    """publish project in PyPI"""


@task
def publish_docs():
    """publish project's documentation."""


@task
def sdist():
    """generate source distribution in .zip and tar.gz formats."""
    pass


@task
def bdist():
    """generate binaries for your architecture and "dumb" binaries."""


@task
def html():
    """build the html documentation under doc/build/html/."""


@task
def read_docs(browser=None):
    """build the documentation and open it using a web browser."""



#
# Testing
#
@task
def test():
    """run the full test suite."""
    pass


@task(py2src)
def py2test():
    """run the full test suite in Python 2."""
    pass


@task
def coverage():
    """run py.test coverage analysis in your code."""


@task
def qa():
    """analyse code quality and how it has changed for your code."""


@task
def smells():
    """look for code smells"""


@task
def benchmark():
    """run benchmarks"""


@task
def cythonize():
    """create pyx and pxi files to C."""


@task
def tox():
    """Run tox"""


@task
def travis():
    """Check status in Travis-CI."""


#
# Git workflow
#
@task
def commit(message="commiting some changes"):
    """commit changes."""


@task
def push():
    """push changes to remote."""


@task
def pull(warn=True):
    """pull changes to remote.

    You should work in your own fork and avoid using this command at all."""

    if warn:
        print("You should work in your own fork and avoid pulling things "
              "directly from upstream.")

@task
def sync():
    """sync your repo with upstream."""