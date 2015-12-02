import manuel.ignore
import manuel.codeblock
import manuel.doctest
import manuel.testing
import pytest
import os


def _factory(func, name):
    """Create a new pytest test function"""

    # Wrap function so pytest do not expect an spurious "self" fixture.
    def wrapped():
        func()

    wrapped.__name__ = name
    return wrapped


def add_manuel_suite():
    """
    Prepare Manuel test suite.
    """

    # Collect documentation files
    test_path = os.path.dirname(__file__)
    mod_path = os.path.dirname(test_path)
    src_path = os.path.dirname(mod_path)
    proj_path = os.path.dirname(src_path)
    doc_path = os.path.join(proj_path, 'doc', 'source')
    files = sorted(os.path.join(doc_path, f) for f in os.listdir(doc_path))
    files = (f for f in files if f.endswith('.rst') or f.endswith('.txt'))

    # Create manuel suite
    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel()
    m += manuel.codeblock.Manuel()

    # Copy tests from the suite to the global namespace
    names = globals()
    suite = manuel.testing.TestSuite(m, *files)
    for i, test in enumerate(suite):
        name = 'test_manuel_example_%s' % i
        names[name] = _factory(test.runTest, name)
    return suite


add_manuel_suite()


if __name__ == '__main__':
    pytest.main('test_documentation.py')
