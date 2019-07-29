import random

import numpy as np

from bonapity import bonapity

@bonapity
def json_serializable_res() -> dict:
    return {
        'this object is' : "JSON Serialisable"
    }

@bonapity
def pickle_serializable_res() -> np.array:
    return np.array([0.])

@bonapity
def surprise_res():
    # Example where we don't know in advance 
    # if the return is in JSON or pickle
    return random.choice([
        "JSON",               # This is JSON Serializable
        np.array(['pickle'])  # This is Pickle Serializable
    ])


if __name__ == "__main__":
    random.seed(0) #to always return `surprise_res` in same order at each run
    bonapity.serve()

