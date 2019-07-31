"""
Example to contact the API in python and get back 
objects in JSON or in pickle binary dump.

Start `np_server_api.py` before running this script.

This script should print something like : 
```
json_serializable_res : {'this object is': 'JSON Serialisable'}
pickle_serializable_res : [0.]
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : JSON
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : ['pickle']
surprise_res : JSON
```
"""
import json
import pickle

import requests


if __name__ == "__main__":
    # Fetch a JSON serializable return
    r = requests.get('http://localhost:8888/json_serializable_res')
    # Request return bytes, we need to decode as string 
    # with the .decode() to be parsed
    res = json.loads(r.content.decode())
    print(f"json_serializable_res : {res}")

    # Fetch a pickle serializable return
    r = requests.get('http://localhost:8888/pickle_serializable_res')
    # pickle need bytes, to we do not have to decode the object
    res = pickle.loads(r.content)
    print(f"pickle_serializable_res : {res}")

    # As return is random do it 10x to see the different results
    for i in range(10):
        # Fetch something we don't know if it's JSON or Pickle serialized
        r = requests.get('http://localhost:8888/surprise_res')
        try:
            # Try to decode as Pickle
            res = pickle.loads(r.content)
        except:
            # If it's not a Pickle dump, it's a JSON (no other choice)
            res = json.loads(r.content.decode())
        print(f"surprise_res : {res}")
