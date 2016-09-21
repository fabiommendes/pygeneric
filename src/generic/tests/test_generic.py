import pytest
import generic


def test_project_defines_author_and_version():
    assert hasattr(generic, '__author__')
    assert hasattr(generic, '__version__')
