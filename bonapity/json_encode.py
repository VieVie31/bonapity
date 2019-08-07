"""
This module contains useful functions to help to generalize
common types and easy user deffined types into JSON

@author: VieVie31
"""
import json
import typing

from copy import deepcopy


class NotRightType(Exception):
    pass

# Decorator
class ObjectToJSONizable:
    __all_transform_functions = []

    def __new__(cls, fun):
        """
        The meta-class construcor is the decorator indexing all possible
        transformations to be applied when `resolve` is called.

        The decored function should return a tuple containing the serialized
        object and a boolean (False by defaut) informing if the result is a
        case base (result JSON serializable).
        """
        ObjectToJSONizable.__all_transform_functions.append(fun)
        return fun

    
    @staticmethod
    def resolve(obj):
        """
        Try ton convert a given object into a JSON serializable
        object (typically `dict`) or die.

        <!> : This function use recursive call and so can be slow, 
        prefer making your object serializable yourself if possible.

        :param obj: the object to try to serialize

        :return: an object which is JSON serializable
        """
        # Copy the object to not destroy it
        obj = deepcopy(obj)

        # Find the right transformation
        out = NotRightType()
        stop_recurstion = False
        for transformation in ObjectToJSONizable.__all_transform_functions:
            try:
                out, stop_recurstion = transformation(obj)
                if not type(out) in [type(None), bool, int, float, str, list, dict]:
                    out = NotRightType()
            except:
                pass

        # No transform function succeedded to transform the object in dict
        if type(out) == NotRightType:
            raise NotRightType(f"Didn't succeed to JSON encode : {out}")
        else:
            # Try to encode it (for exemple numpy array may 
            # - somtimes - be directly encoded, no recursion needed)
            try:
                out, stop_recurstion = transform_default_json_encoder(out)
            except:
                pass
        
        # If allowed to stop recursion, return result as is
        if stop_recurstion:
            return out
        
        # Continue to make each 
        if type(out) == dict:
            for k in out:
                out[k] = ObjectToJSONizable.resolve(out[k])
            return out
        elif type(out) == list:
            for i in range(len(out)):
                out[i] = ObjectToJSONizable.resolve(out[i])
            return out
        else:
            raise Exception(f"Type {type(out)} unexpected in resolve...")

@ObjectToJSONizable
def transform_default_json_encoder(obj) -> typing.Tuple[typing.Dict, bool]:
    """
    Try to encode the object with the default python json encoder.
    If success, we do not need to do any more recursive call.
    This is a base case. 
    The First returned value can not be a dict but a JSON serializable object
    such as list or int.
    """
    return json.loads(json.dumps(obj)), True

@ObjectToJSONizable
def transform_numpy(ndarray) -> typing.Tuple[typing.List, bool]:
    return ndarray.tolist(), False
    
@ObjectToJSONizable
def transform_simple_object(obj) -> typing.Tuple[typing.Dict, bool]:
    return obj.__dict__, False


@ObjectToJSONizable
def transform_python_sets(_set) -> typing.Tuple[typing.List, bool]:
    return list(_set)


#TODO: transform other generic types such as sets, dates
# or complex ones such as plots
    
class BonapityJSONEncoder(json.JSONEncoder):
    """
    This class inherit from json.JSONEncoder and can be used as bellow :
    ```python
    >>> json.dumps(myobject, cls=BonapityJSONEncoder)
    ```
    """
    def default(self, obj):
        return ObjectToJSONizable.resolve(obj)

