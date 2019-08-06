"""
Get a simple HTTP (REST) API with only this simple decorator : `@bonapity` !
See documentation with : `help(bonapity)`.

@author: VieVie31
"""
from .decorators import bonapity, vuosi

__version_info__ = (0, 1, 18)
__version__ = '.'.join(map(str, __version_info__))
__author__ = "Olivier RISSER-MAROIX (VieVie31)\nAdrien POUYET (Ricocotam)"

__all__ = ["bonapity", "vuosi"]
