from .meta import __author__, __version__
from .errors import *
from .conversion import *
from .core import *
from . import op
from .op import Object

#
# Import some types from Python stdlib that can be useful in defining generic
# functions
#

# Abstract Collections
from abc import *
from numbers import *

# Types
import types as _types
globals().update({name: tt
                for (name, tt) in vars(_types).items() if name.endswith('Type')})
