import sys
from invoke import run, task
from python_boilerplate.tasks import *
import configparser

py3to2_fixes = [
    'newstyle', 'kwargs', 'division', 'metaclass', 'unpacking', 'super',
    'annotations',
]

@task
def configure(ctx):
    """
    Instructions for preparing package for development.
    """

    run("%s -m pip install .[dev] -r requirements.txt" % sys.executable)


@task
def py2src(ctx):
    """
    update the Python 2 source tree at py2src.
    """

    # Get all fixes
    fixes = ' '.join('-f %s' % fix for fix in py3to2_fixes)

    # Move source to py2src folder and patch encoding
    run('cp src/ py2src/ -R')
    run('3to2 py2src/ --no-diffs -j4 -w %s' % fixes)

