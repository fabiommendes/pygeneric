'''
Register all built-in conversion and promotion rules.
'''
from ..errors import InexactError
from . import set_conversion, set_promotion_rule

###############################################################################
#                             Conversion rules
###############################################################################
set_conversion(int, float, float)
set_conversion(int, complex, complex)
set_conversion(float, complex, complex)


@set_conversion(float, bool)
@set_conversion(int, bool)
@set_conversion(complex, bool)
def number2bool(x):
    if x == 0:
        return False
    elif x == 1:
        return True
    else:
        raise InexactError(x)


@set_conversion(complex, int)
@set_conversion(float, int)
def number2int(x):
    out = int(x)
    if out == x:
        return out
    else:
        raise InexactError(x)

###############################################################################
#                               Promotion rules
###############################################################################
set_promotion_rule(int, float, float)
set_promotion_rule(int, complex, complex)
set_promotion_rule(float, complex, complex)
