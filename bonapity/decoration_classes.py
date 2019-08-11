"""
This module contains the classes used internally
to store and manage the decorated functions.

@author: VieVie31
"""
import json
import typing

from dataclasses import dataclass

from .json_encode import BonapityJSONEncoder


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
    mime_type: str = "auto"
    json_encoder: json.JSONEncoder = BonapityJSONEncoder


class BonapityException(Exception):
    """
    Bonapity Exception, usefull for the `vuosi` decorator to differentiate
    exceptions from `bonapity` (server communication for example) from others.
    """
    pass
