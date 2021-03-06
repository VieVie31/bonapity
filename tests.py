"""
Skeleton for unitesting bonapity.

TODO: complete
"""
import unittest

import time
import queue
import threading

import json
import pickle
import typing
import functools

import urllib

from http.server import BaseHTTPRequestHandler, HTTPServer

from bonapity import bonapity
from bonapity.server import BonAppServer
from bonapity.decoration_classes import BonapityException

DOMAIN = 'localhost'
PORT = 8889

# Define a bunch of bonapity function to test

@bonapity
def test_no_param():
    return True

@bonapity
def test_add(a: int, b: int) -> int:
    return a + b

@bonapity
def test_concatenate(a: str, b: str) -> str:
    return a + b

@bonapity
def test_sum_list_int(L: typing.List[int]) -> int:
    return sum(L)

@bonapity(timeout=1)
def test_timeout_crash():
    time.sleep(2)
    return True

@bonapity(timeout=0)
def test_no_timeout():
    time.sleep(10)
    return True

@bonapity
def test_default_arg(a=5):
    return a

@bonapity
def test_args_kargs(*a, **k):
    return (type(a) in [type([]), type((0,))]) and type(k) == type({})

@bonapity
def test_return_json_serializable_object():
    return {'a': ["coucou", 1, 4, {'inner_a': 'ok'}], 'b': 6.5}

@bonapity
def test_return_non_json_serializable_type():
    class A: 
        def __init__(self, v):
            self.v = v
    return A(42)

@bonapity(name='test_changing_fname')
def coucou():
    return True


# Define helpful function for different data transfert and timeout

def execute_function_with_timeout(fun, timeout=2):
    """
    Execute a function w/o argument (or pre filled with partial)
    and return result in less than `timeout` seconds, else raise Exception

    :param fun: function w/o argument (or pre filled w partial) to execute
    :param timeout: number of seconds allowed for the function execution
    """
    que = queue.Queue()
    thr = threading.Thread(target=lambda q: q.put(fun()), args=(que,))
    thr.start()
    thr.join(timeout)

    if que.empty():
        raise Exception("Timeout")
    else:
        return que.get()


def send_as_url_query(fun_api_name, data):
    raise NotImplementedError()

def send_as_get_json(fun_api_name, data):
    raise NotImplementedError()

def send_as_post_json(fun_api_name, data):
    raise NotImplementedError()

def send_as_post_pickle(fun_api_name, params):
    params = pickle.dumps(params)
    r = urllib.request.urlopen(urllib.request.Request(
        f'http://{DOMAIN}:{PORT}/{fun_api_name.__name__}',
        data=params,
        headers={"Content-Type": "application/python-pickle"}
    ))
    if r.status != 200:
        raise Exception(
            f"Failed to fetch result, code : [{r.status}], message : {r.read()}"
        )
    res = r.read()
    try:
        res = pickle.loads(res)
    except:
        res = json.loads(res.decode())
    return res


# Define the test cases

class TestBonAppServer(unittest.TestCase):
    """
    Test the different data input/output of BonAppServer
    """

    """def test_send_as_url_query(self):
        raise NotImplementedError()
    
    def test_send_as_get_json(self):
        raise NotImplementedError()

    def test_send_as_post_json(self):
        raise NotImplementedError()
    """
    def test_send_as_post_pickle(self):
        assert send_as_post_pickle(test_no_param, {}) == test_no_param()
        assert send_as_post_pickle(test_add, {'a': 4, 'b': 5}) == test_add(4, 5)
        assert send_as_post_pickle(test_concatenate, {'a': 'cou', 'b': 'cou'}) == test_concatenate('cou', 'cou')
        assert send_as_post_pickle(test_concatenate, {'a': 2, 'b': 3}) == test_concatenate('2', '3')
        assert send_as_post_pickle(test_sum_list_int, {'L': [1, 2, 3]}) == test_sum_list_int([1, 2, 3])
        assert send_as_post_pickle(test_no_timeout, {})
        assert send_as_post_pickle(test_default_arg, {}) == test_default_arg()
        assert send_as_post_pickle(
            test_args_kargs, {'a': (1, 2, 3), 'k': {'a': 1, 'b': 2}}
        ) == test_args_kargs(*(1, 2, 3), a=1, b=2)
        # TODO: implement tests on the following functions
        #test_timeout_crash
        #test_return_json_serializable_object
        #test_return_non_json_serializable_type
        #test_changing_fname




if __name__ == '__main__':
    # Start the test server in a parallel thread
    bonapity_partial_serve_function = functools.partial(
        bonapity.serve, **{'port': PORT, 'timeout': 5})
    bonapity_server_thread = threading.Thread(
        target=bonapity_partial_serve_function)
    bonapity_server_thread.start()

    # Run tests
    unittest.main()

