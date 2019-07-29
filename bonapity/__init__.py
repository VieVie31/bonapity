"""
Get a simple HTTP (GET) API with only this simple decorator : `@bonapity` !
See documentation with : `help(bonapity)`.

@author: VieVie31
"""
import ast
import typing
import inspect
import functools

import cgi
import html
import json
import http.server
import urllib.parse

import base64
import pickle

from types import MethodType
from collections import defaultdict, OrderedDict

__all__ = ["bonapity"]
__decorated = {}

class BonAppServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kargs):
        super(BonAppServer, self).__init__(*args, **kargs)
        self.help = True

    def process(self, parameters):
        """
        This method do the common stuffs between do_GET and do_POST.

        :param parameters: key-value dict of parameters (values are not parsed)
        """
        __decorated = globals()["__decorated"]

        parsed_url = urllib.parse.urlparse(self.path)

        fun = __decorated[parsed_url.path]
        sig = inspect.signature(fun)
        

        # Check if parameters names matches 
        # (and ignore default and *args, **kargs parameters)
        full_arg_spec = inspect.getfullargspec(fun)
        ignored_params_names = list(filter(
            lambda k: sig.parameters[k].default != inspect._empty or \
                 k == full_arg_spec.varargs or k == full_arg_spec.varkw,
            sig.parameters.keys()
        ))
        
        if sorted(set(sig.parameters.keys()) - set(ignored_params_names)) \
          != sorted(set(parameters.keys()) - set(ignored_params_names)):
            self.send_response(400)
            self.send_header('Content-type','text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b"Parameters names do not match the signature of the function...")
            return

        #try
        for param_key, param_value in parameters.items():
            if len(param_value) != 1:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b"Each argument can be used only once !")
                return
            
            param_value = param_value[0]
            
            ftype = sig.parameters[param_key].annotation

            if ftype != str:
                # Try to evaluate
                evaluated = False
                try:
                    # Evaluate as Python formated text
                    param_value = ast.literal_eval(param_value)
                    evaluated = True
                except:
                    pass
                
                try:
                    # Evalutate as JONS formated text
                    if not evaluated:
                        param_value = json.loads(param_value)
                        evaluated = True
                except:
                    pass
                
                # Return 500 error if failed to evaluate parameter
                if not evaluated:
                    self.send_response(500)
                    self.send_header('Content-type','application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f"Parameter {param_key} : {param_value} poorly formated...".encode())
                    return

                # Try to cast
                if ftype == inspect._empty:
                    # No typing 
                    # just affect the parsed value
                    parameters[param_key] = param_value
                else:
                    supported_generic_types = {
                        int: int(),
                        float: float(),
                        str: str(),
                        bool: bool(),
                        typing.List[(ftype.__args__[0],) if '__args__' in ftype.__dict__ else None]: list(),
                        typing.Tuple[(ftype.__args__[0],) if '__args__' in ftype.__dict__ else None]: tuple(),
                        typing.Set[(ftype.__args__[0],) if '__args__' in ftype.__dict__ else None]: set(),
                        typing.FrozenSet[(ftype.__args__[0],) if '__args__' in ftype.__dict__ else None]: frozenset(),
                        typing.Dict[ftype.__args__ if '__args__' in ftype.__dict__ and len(ftype.__args__) == 2 else (None, None)]: dict()
                    }
                    if ftype in supported_generic_types:
                        # Cast the generic type
                        try:
                            parameters[param_key] = type(supported_generic_types[ftype])(param_value)
                        except Exception as e:
                            self.send_response(500)
                            self.send_header('Content-type','application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(f"Error on parameter `{param_key}` : {e}".encode())
                            return
                    else:
                        # Not a generic python type : 
                        # just affect the parsed value
                        parameters[param_key] = param_value
            else:
                # ftype was str
                parameters[param_key] = str(param_value)


        # Execute the function or die
        try:
            # Fill the first positional arguments in the right order
            f = functools.partial(
                fun,
                *[parameters[a] for a in inspect.getfullargspec(fun).args]
            )

            # Fill the *args if any
            if full_arg_spec.varargs != None and len(full_arg_spec.varargs):
                f = functools.partial(f, *parameters[full_arg_spec.varargs])

            # Fill the **kargs if any
            if full_arg_spec.varkw != None and len(full_arg_spec.varkw):
                f = functools.partial(f, **parameters[full_arg_spec.varkw])
           
            res = f()
            
            # Ecode result in JSON
            try:
                res = json.dumps(res)

                # Send success
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(
                    f"{res}".encode()
                )
                return
            except Exception as e:
                # Encore into pickle and send a binary object
                try:
                    res = pickle.dumps(res)
                    
                    # Send success
                    self.send_response(200)
                    self.send_header('Content-type','application/python-pickle')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(res)
                    return
                except Exception as nested_e:
                    e = nested_e
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"TypeError on {fun.__name__} : {e}, result is not serializable (JSON nor pickle)... :'(".encode())
                return

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f"Error in {fun.__name__} : {str(e)}".encode())
            return


    def do_GET(self):
        __decorated = globals()["__decorated"]

        parsed_url = urllib.parse.urlparse(self.path)
        
        # Check if display help
        if self.help and (parsed_url.path.startswith('/help/') or parsed_url.path in ['', '/']):
            fname = parsed_url.path[5:]
            
            # If no name given, make an index of all functions allowed in the API
            if fname in ['', '/', '/*']:
                modules = defaultdict(list)
                for fname in __decorated.keys():
                    modules[__decorated[fname].__module__].append(fname)

                html_out = f"""
                    <h1>Index of functions available in the API</h1><hr>
                    {''.join([
                        f'''
                            <h2>{m}</h2>
                            <u>
                                {
                                    ''.join([
                                        f'<li><a href="/help{f}">{f}</a></li>'
                                        for f in modules[m]
                                    ])
                                }
                            </ul>
                            <hr>
                        '''
                        for m in modules
                    ])}
                    <div style="position:absolute;bottom:5;right:5;">
                    <hr><footer>Auto generated by 
                    ★ <a href='https://github.com/VieVie31/bonapity'>bonAPIty</a> ★
                    </footer></div>
                """

                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(html_out.encode())
                return
            elif not self.help and parsed_url.path == '/':
                self.send_response(404)
                self.send_header('Content-type','text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'')
                return

            if not fname in __decorated.keys():
                self.send_response(404)
                self.send_header('Content-type','text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"{fname} : this function do not exists...".encode())
                return
            fun = __decorated[fname]
            sig = html.escape(f"{fun.__name__}{inspect.signature(fun)}")
            doc = html.escape(fun.__doc__) if fun.__doc__ else ''
            html_out = f"""
                <h1>Documentation for : {fname}</h1>
                <div>Signature : <i><tt>{sig}</tt></i></div><hr>
                <div><code style='display:block;white-space:pre-wrap'>{doc}</code></div>
                <div style="position:absolute;bottom:5;right:5;">
                <hr><footer>Auto generated by 
                ★ <a href='https://github.com/VieVie31/bonapity'>bonAPIty</a> ★
                </footer></div>
            """
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html_out.encode())
            return
        
        #Check if the function the user want to call exists
        if not parsed_url.path in __decorated.keys():
            self.send_response(404)
            self.send_header('Content-type','text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f"{parsed_url.path} : this function do not exists...".encode())
            return

        #TODO: check if unique parameter without value
        #  ==> process as base64 pickled object : decode parameters from it

        # Handle API
        parameters = urllib.parse.parse_qs(
            parsed_url.query
        )

        self.process(parameters)
        return 
        
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={
                'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            }
        )
        #TODO: handle JSON vs pickle Content-Type
        parameters = {k: form[k].value for k in form} #cgi.MiniFieldStorage
        self.process(parameters)
        return

def serve(self, port=8888, help=True):
    """
    Serve your API forever.

    :param port:
        the port to serve the API
    :param help:
        return the documentation of functions at 
        `http://[SERVER]/help/[FUN_NAME|ROOT]`

    :type port: int
    :type help: bool

    Example :
    ```
    >>> bonapity.serve(8080)
    Server running on  port : 8080
    ```
    """
    global __decorated
    PORT = port
    server_address = ("", PORT)
    server = http.server.HTTPServer
    handler = BonAppServer

    print(f"Server running on  port : {PORT}")
    httpd = server(server_address, handler)

    httpd.RequestHandlerClass.bonapity = self
    httpd.RequestHandlerClass.help = help

    httpd.serve_forever()

def bonapity(fun=None, name: str=None):
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
    global __decorated
    if fun is None:
        return functools.partial(
            bonapity, name=name
        )
    elif type(fun) == str:
        return functools.partial(
            bonapity, name=fun
        )

    fname = fun.__name__ if not name else name
    fname = f"{'' if fname[0] == '/' else '/'}{fname}"
    __decorated[fname] = fun
    
    @functools.wraps(fun)
    def f(*args, **kwargs):
        return fun(*args, **kwargs)
    return f


bonapity.serve = MethodType(serve, bonapity)


