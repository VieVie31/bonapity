"""
Get a simple HTTP (REST) API with only this simple decorator : `@bonapity` !
See documentation with : `help(bonapity)`.

@author: VieVie31
"""
from .decoration_classes import *
from .code_generation import *
from .decorators import *

__version_info__ = (0, 1, 11)
__version__ = '.'.join(map(str, __version_info__))
__author__ = "Olivier RISSER-MAROIX (VieVie31)"

__all__ = ["bonapity", "vuosi"]



