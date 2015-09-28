'''
Holds all special error classes defined for the generic module.
'''


class InexactError(ValueError):
    '''Raised on conversion of float values with decimal places to integer
    types'''
