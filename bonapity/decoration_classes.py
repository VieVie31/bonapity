"""
This module contains the classes used internally
to store and manage the decorated functions.

@author: VieVie31
"""
import typing

from dataclasses import dataclass


class DecoratedFunctions(object):
    """
    This static class contains the listing of all functions decorated.
    """
    all = {}

    def __new__(cls):
        return DecoratedFunctions.all


@dataclass
class BonapityDecoratedFunction():
    """
    This class store the function and the timeout allowed for it.
    """
    fun: typing.Callable
    timeout: int = 0
