"""
This module contains all the functions which will be converted into decorators.

@author: VieVie31, Ricocotam
"""
import json
import pickle
import urllib
import functools
import contextvars
import http.cookies

from .server import ThreadingBonAppServer, BonAppServer
from .decoration_classes import DecoratedFunctions, BonapityDecoratedFunction, BonapityException
from .json_encode import BonapityJSONEncoder
from .session import SessionManager

__all__ = ["bonapity", "vuosi"]


def vuosi(domain: str, port: int):
    """
    Decorator for python clients to simplify the requests data transfert
    and using the API like a bunch of blackbox functions...

    The decored function name should be a command of the api.
    Example:
    ```
    >>> @vuosi('localhost', 8888) # Specify the domain and the port
    >>> def myfun(a):
    ...     # Can create this function only if `/myfun?a=...` exists in the api
    ...     pass # No body needed, the decorator will write/execute is for you

    >>> myfun('coucou cici')
    ```
    """

    def inner_vuosi(fun):
        def fetch(**params):
            """
            All arguments are keyword arguments...
            For example do not write f(3) but f(x=3)...
            """
            params = pickle.dumps(params)
            r = urllib.request.urlopen(urllib.request.Request(
                f'http://{domain}:{port}/{fun.__name__}',
                data=params,
                headers={"Content-Type": "application/python-pickle"}
            ))
            if r.status >= 300:
                raise BonapityException(
                    f"Failed to fetch result, code : [{r.status}], message : {r.read()}"
                )
            res = r.read()
            # print(res)
            try:
                res = pickle.loads(res)
            except:
                res = json.loads(res.decode())
            return res

        fetch.__name__ == fun.__name__
        return fetch

    return inner_vuosi


class MetaBonAPIty(type):
    @property
    def cookies(cls):
        return cls._BonAPIty__cookies.get()
    
    @property
    def session(cls):
        return cls._BonAPIty__session.get()

class BonAPIty(object, metaclass=MetaBonAPIty):
    # Each function will have access to the current client cookies
    # with `BonAPIty.cookies.get()`. The content of the variable w'll be
    # changed updated with the contextvars
    __cookies = contextvars.ContextVar("bonapity.cookies")
    __session = contextvars.ContextVar("bonapity.session")

    @staticmethod
    def __exec_function(f, cookies=http.cookies.SimpleCookie(), session={}):
        global bonapity
        context = contextvars.copy_context()
        context.run(bonapity._BonAPIty__cookies.set, cookies)
        context.run(bonapity._BonAPIty__session.set, session)
        res = context.run(f)
        return res, context.get(bonapity.__cookies)

    @staticmethod
    def serve(
        port=8888, static_files_dir: str = './', index: str = None, 
        help: bool = True, timeout: int = 10, session_timeout: int = 600, 
        verbose: bool = True):
        """
        Serve your API forever.

        :param port:
            the port to serve the API
        :param static_files_dir:
            root of the directory to serve as static files
            (those files are served as GET only)
            prefer absolute path, less ambiguous (
                else depend of the current position of python
                ) => less problems
        :param index:
            if not None, use this page as index (returned as html)
        :param help:
            return the documentation of functions at
            `http://[SERVER]/help/[FUN_NAME|ROOT]`
        :param timeout:
            number of seconds before ending the function and returning
            timeout error message, if 0, no timeout is applied
        :param verbose:
            display some informations such as the port where the server w'll run

        :type port: int
        :type help: bool

        Example :
        ```
        >>> bonapity.serve(8080)
        Server running on  port : 8080
        ```
        """
        SessionManager.session_timeout = session_timeout

        PORT = port
        server_address = ("", PORT)
        handler = BonAppServer

        if verbose:
            print(f"Server running on  port : {PORT}")

        httpd = ThreadingBonAppServer(server_address, handler)

        httpd.RequestHandlerClass.bonapity = BonAPIty
        httpd.RequestHandlerClass.port = port

        httpd.RequestHandlerClass.static_files_dir = static_files_dir
        httpd.RequestHandlerClass.index = index
        httpd.RequestHandlerClass.help = help
        httpd.RequestHandlerClass.default_timeout = timeout

        httpd.RequestHandlerClass.cookies_context = contextvars.copy_context()
        

        httpd.serve_forever()

    @staticmethod
    def __new__(
        cls, fun=None, name: str = None, 
        timeout: int = None, mime_type: str = "auto", 
        json_encoder: json.JSONEncoder = BonapityJSONEncoder):
        """
        Get a simple HTTP GET API with this simple decorator.
        You'll be able to use your function at :
        `http://[SERVER]/[FUN_NAME|ALIAS_NAME]?[PARAMETERS]`.

        To start the server use the `serve` method.

        :param fun:
            the function we want to create a simple api
            it's safer to use type hints for input args
            we w'll cast the inputs for you
            the types should be python generics ones
        :param name:
            rename this function in the api to conflict names
        :param timeout:
            timeout to kill the function
        :param mime_type:
            specity your return mine-type if you want to return
            custom data such as binary images. If content-type
            given, the function is assumed returning byte data.
            If mine_type is set to "auto" (default) AND your
            function return type is `byte` we try to automatically
            detect the right mime type.
        :param json_encoder:
            the encoder to use when trying to serialize
            the return type as json, the default `BonapityJSONEncoder`
            is slower as it can handle more complex object than
            the default encoder, you can change it by the default
            `json.JSONEncoder` or your one encoder inheriting from it.
            Remember, if the encoder can't encode the object into
            a JSON format, the object returned will be pickled.

        Example:
        ```
        >>> from bonapity import bonapity

        >>> @bonapity      #or @bonapity('my_alias_fun_name')
        ... def add(a: int, b: int=0) -> int:
        ...     return a + b

        >>> if __name__ == '__main__':
        ...     bonapity.serve()
        ```
        """
        if fun is None:
            return functools.partial(
                BonAPIty.__new__, cls, name=name, timeout=timeout,
                mime_type=mime_type, json_encoder=json_encoder
            )
        elif type(fun) == str:
            return functools.partial(
                BonAPIty.__new__, cls, name=fun, timeout=timeout,
                mime_type=mime_type, json_encoder=json_encoder
            )

        fname = fun.__name__ if not name else name
        fname = f"{'' if fname[0] == '/' else '/'}{fname}"
        DecoratedFunctions.all[fname] = BonapityDecoratedFunction(
            fun, timeout, mime_type, json_encoder)

        @functools.wraps(fun)
        def f(*args, **kwargs):
            return fun(*args, **kwargs)

        return f


bonapity = BonAPIty
