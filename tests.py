"""
Skeleton for unitesting bonapity.

TODO: complete
"""
import unittest

import time
import queue
import threading

import pickle
import typing
import functools

from http.server import BaseHTTPRequestHandler, HTTPServer

from bonapity import bonapity
from bonapity.server import BonAppServer

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
    return sum(test_sum_list_int)

@bonapity(timeout=1)
def test_timeout_crash():
    time.sleep(2)
    return False

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

def send_as_json(fun_api_name, data):
    raise NotImplementedError()

def send_as_pickle(fun_api_name, data):
    raise NotImplementedError()


# Define the test cases

class TestBonAppServer(unittest.TestCase):
    """
    Test the different data input/output of BonAppServer
    """

    def test_send_as_url_query(self):
        raise NotImplementedError()
    
    def test_send_as_json(self):
        raise NotImplementedError()
    
    def send_as_pickle(self):
        raise NotADirectoryError()


if __name__ == '__main__':
    # Start the test server in a parallel thread
    bonapity_partial_serve_function = functools.partial(
        bonapity.serve, **{'port': 8889, 'timeout': 5})
    bonapity_server_thread = threading.Thread(
        target=bonapity_partial_serve_function)
    bonapity_server_thread.start()

    # Run tests
    unittest.main()

