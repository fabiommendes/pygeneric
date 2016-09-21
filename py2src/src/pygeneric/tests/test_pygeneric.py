import pytest
import pygeneric


def test_project_defines_author_and_version():
    assert hasattr(pygeneric, '__author__')
    assert hasattr(pygeneric, '__version__')
