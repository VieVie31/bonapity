"""
This module contains all the functions which will be converted into decorators.

@author: VieVie31, Ricocotam
"""
import json
import pickle
import urllib
import functools

from .server import ThreadingBonAppServer, BonAppServer
from .decoration_classes import DecoratedFunctions, BonapityDecoratedFunction, BonapityException

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


class BonAPIty:
    _singleton = None

    def __new__(cls, fun=None, name: str = None, timeout: int = None, mime_type: str = "auto"):
        cls.get_singleton()

        return cls._singleton.new_function(fun, name, timeout, mime_type)

    @staticmethod
    def get_singleton():
        if BonAPIty._singleton is None:
            BonAPIty._singleton = object.__new__(BonAPIty)
        return BonAPIty._singleton

    def __init__(self):
        print("init")
        self.server = None

    def start_server(self, port=8888, static_files_dir: str = './', index: str = None, help: bool = True, timeout: int = 10, verbose: bool = True):
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
        if self.server is not None:
            return
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

        httpd.serve_forever()
        self.server = httpd

    @staticmethod
    def serve(port=8888, static_files_dir: str = './', index: str = None, help: bool = True, timeout: int = 10, verbose: bool = True):
        BonAPIty.get_singleton().start_server(port, static_files_dir, index, help, timeout, verbose)

    @staticmethod
    def stop():
        BonAPIty.get_singleton().stop_server()

    def stop_server(self):
        if self.server is not None:
            self.server.shutdown()

    def new_function(self, fun=None, name: str = None, timeout: int = None, mime_type: str = "auto"):
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
                BonAPIty.__new__, BonAPIty, name=name, timeout=timeout,
                mime_type=mime_type
            )
        elif type(fun) == str:
            return functools.partial(
                BonAPIty.__new__, BonAPIty, name=fun, timeout=timeout,
                mime_type=mime_type
            )

        fname = fun.__name__ if not name else name
        fname = f"{'' if fname[0] == '/' else '/'}{fname}"
        DecoratedFunctions.all[fname] = BonapityDecoratedFunction(
            fun, timeout, mime_type)

        @functools.wraps(fun)
        def f(*args, **kwargs):
            return fun(*args, **kwargs)

        return f


bonapity = BonAPIty
