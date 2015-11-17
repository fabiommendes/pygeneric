"""
Loads all tests in module and run
"""

if __name__ == '__main__':
    from pytest import main
    main('-q --doctest-modules')
