from .core import generic, overload
from .conversion import *
from . import op

#
# Import some types from Python stdlib that can be useful in defining generic
# functions
#

# Abstract Collections
from collections.abc import *
from numbers import *

# Types
import types as _types
globals.update({name: tt
                for (name, tt) in _types.items() if name.endswith('Type')})
