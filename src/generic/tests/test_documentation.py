import manuel.ignore
import manuel.codeblock
import manuel.doctest
import manuel.testing
import pytest
import os


# TODO: integrate manuel with py.test

def add_manuel_suite(D):
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

    # Add tests to the global namespace
    suite = manuel.testing.TestSuite(m, *files)
    for i, test in enumerate(suite):
        key = 'test_manuel_%s' % i
        D[key] = test
    return suite


add_manuel_suite(globals())

if __name__ == '__main__':
    import unittest

    unittest.TextTestRunner().run(add_manuel_suite({}))
    pytest.main('test_documentation.py')