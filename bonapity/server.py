"""
This module contains all stuffs to handle the HTTP server.

@author: VieVie31
"""
import ast
import typing
import inspect
import functools
import html
import json
import base64
import pickle
import http.server
import urllib.parse
import urllib.request
import socketserver

from collections import defaultdict
from multiprocessing import Process, Manager

from .code_generation import generate_js, generate_python
from .decoration_classes import DecoratedFunctions


def send_header(server_instance, code, content_type):
    """
    This function is used by the BonAppServer to send back the headers.

    :param server_instance:
        the instance of the BonAppServer (should call with `self`)
    :param code:
        the HTTP code status to return
    :param content_type:
        the HTTP `Content-Type` information (eg. txt/html, application/json)
    """
    server_instance.send_response(code)
    server_instance.send_header('Content-type', content_type)
    server_instance.send_header(
        "Access-Control-Allow-Origin",
        'null'
        if server_instance.headers["Origin"] is None
        else server_instance.headers["Origin"]
    )
    server_instance.send_header(
        'Access-Control-Allow-Methods',
        'GET, POST, PUT, DELETE, PATCH, OPTIONS'  # *?
    )
    server_instance.send_header("Access-Control-Allow-Credentials", 'true')
    server_instance.end_headers()


class BonAppServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kargs):
        super(BonAppServer, self).__init__(*args, **kargs)
        self.help = True
        self.port = 80
        self.default_timeout = 1

    def process(self, parameters, value_already_evaluated=False):
        """
        This method do the common stuffs between do_GET and do_POST.

        :param parameters: key-value dict of parameters (values are not parsed)
        """
        parsed_url = urllib.parse.urlparse(self.path)

        # Get the function in the decorated function list
        fun = DecoratedFunctions.all[parsed_url.path].fun
        sig = inspect.signature(fun)

        # Get the timeout informatin of the function, is None set a default one
        timeout = DecoratedFunctions.all[parsed_url.path].timeout
        if timeout is None:
            timeout = self.default_timeout

        # Check if parameters names matches
        # (and ignore default and *args, **kargs parameters)
        full_arg_spec = inspect.getfullargspec(fun)
        ignored_params_names = [
            k for k in sig.parameters.keys()
            if sig.parameters[k].default != inspect._empty
               or k == full_arg_spec.varargs
               or k == full_arg_spec.varkw
        ]

        list(filter(
            lambda k: sig.parameters[k].default != inspect._empty or k == full_arg_spec.varargs or k == full_arg_spec.varkw,
            sig.parameters.keys()
        ))

        if sorted(set(sig.parameters.keys()) - set(ignored_params_names)) \
                != sorted(set(parameters.keys()) - set(ignored_params_names)):
            send_header(self, 400, 'text/html')
            self.wfile.write(
                b"Parameters names do not match the signature of the function...")
            return

        # try
        for param_key, param_value in parameters.items():
            # print("param:", param_key, param_value)
            if len(param_value) != 1:
                send_header(self, 500, 'application/json')
                self.wfile.write(b"Each argument can be used only once !")
                return

            param_value = param_value[0]

            ftype = sig.parameters[param_key].annotation

            if ftype != str:
                # Try to evaluate
                evaluated = value_already_evaluated

                try:
                    # Evaluate as Python formated text
                    if not evaluated:
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
                    send_header(self, 500, 'application/json')
                    self.wfile.write(
                        f"Parameter {param_key} : {param_value} {type(param_value)} poorly formated...".encode())
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
                        typing.Dict[ftype.__args__ if '__args__' in ftype.__dict__ and len(
                            ftype.__args__) == 2 else (None, None)]: dict()
                    }
                    if ftype in supported_generic_types:
                        # Cast the generic type
                        try:
                            parameters[param_key] = type(
                                supported_generic_types[ftype])(param_value)
                        except Exception as e:
                            send_header(self, 500, 'application/json')
                            self.wfile.write(
                                f"Error on parameter `{param_key}` : {e}".encode())
                            return
                    else:
                        # Not a generic python type :
                        # just affect the parsed value
                        parameters[param_key] = param_value
            else:
                # ftype was str
                parameters[param_key] = str(param_value)

        # Add the missing default parameters if not filled
        for k in sig.parameters.keys():
            if k not in parameters:
                parameters[k] = sig.parameters[k].default

        # Execute the function or die
        try:
            # Fill the first positional arguments in the right order
            f = functools.partial(
                fun,
                *[parameters[a] for a in inspect.getfullargspec(fun).args]
            )

            # Fill the *args if any
            if full_arg_spec.varargs is not None and len(full_arg_spec.varargs):
                f = functools.partial(f, *parameters[full_arg_spec.varargs])

            # Fill the **kargs if any
            if full_arg_spec.varkw is not None and len(full_arg_spec.varkw):
                f = functools.partial(f, **parameters[full_arg_spec.varkw])

            if timeout > 0.:
                # Create shared variable wich will contain the result function
                manager = Manager()
                return_dict = manager.dict()

                def execute_and_save_result(fun, return_dict):
                    # Ececute the tunction and store result in shared memory
                    return_dict[0] = fun()

                # Create a process
                action_process = Process(
                    target=execute_and_save_result,
                    args=(f, return_dict)
                )

                # Start the process and we block for the required timeout
                action_process.start()
                action_process.join(timeout=timeout)

                # Terminate the process
                action_process.terminate()

                if 0 in return_dict:
                    # Get result from shared memory
                    res = return_dict[0]
                else:
                    # Time out error
                    send_header(self, 500, 'text/html')
                    self.wfile.write(
                        f"""Timeout error: execution of {fun.__name__}
                        took more than the {self.timeout} allowed seconds
                        """.encode()
                    )
                    return
            else:
                # No timeout constraint
                res = f()

            # Ecode result in JSON
            try:
                res = json.dumps(res)

                # Send success
                send_header(self, 200, 'application/json')
                self.wfile.write(
                    f"{res}".encode()
                )
                return
            except Exception as e:
                # Encore into pickle and send a binary object
                try:
                    res = pickle.dumps(res)

                    # Send success
                    send_header(self, 200, 'application/python-pickle')
                    self.wfile.write(res)
                    return
                except Exception as nested_e:
                    e = nested_e
                send_header(self, 500, 'application/json')
                self.wfile.write(
                    f"TypeError on {fun.__name__} : {e}, result is not serializable (JSON nor pickle)... :'(".encode())
                return

        except Exception as e:
            send_header(self, 500, 'application/json')
            self.wfile.write(f"Error in {fun.__name__} : {str(e)}".encode())
            return

    def do_OPTIONS(self):
        # Send back informations for complex POST
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Methods',
                         self.headers["Access-Control-Request-Method"])
        self.send_header("Access-Control-Allow-Headers",
                         self.headers["Access-Control-Request-Headers"])
        self.send_header(
            "Access-Control-Allow-Origin",
            'null' if self.headers["Origin"] is None
            else self.headers["Origin"]
        )
        self.send_header("Access-Control-Allow-Credentials", 'true')
        self.end_headers()
        # <!> : this method should not contain anything more and no return !

    def do_GET(self):

        parsed_url = urllib.parse.urlparse(self.path)

        # Check if display help
        if self.help and (parsed_url.path.startswith('/help/') or parsed_url.path in ['', '/']):
            fname = parsed_url.path[5:]

            # If no name given, make an index of all functions allowed in the API
            if fname in ['', '/', '/*']:
                modules = defaultdict(list)
                for fname in DecoratedFunctions.all.keys():
                    modules[DecoratedFunctions.all[fname].fun.__module__].append(
                        fname)

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

                send_header(self, 200, 'text/html')
                self.wfile.write(html_out.encode())
                return
            elif not self.help and parsed_url.path == '/':
                send_header(self, 404, 'text/html')
                self.wfile.write(b'')
                return

            if fname not in DecoratedFunctions.all.keys():
                send_header(self, 404, 'text/html')
                self.wfile.write(
                    f"{fname} : this function do not exists...".encode())
                return
            fun = DecoratedFunctions.all[fname].fun
            sig = html.escape(f"{fun.__name__}{inspect.signature(fun)}")
            doc = html.escape(fun.__doc__) if fun.__doc__ else ''
            html_out = f"""
                <h1>Documentation for : {fname}</h1>
                <div><h2>Signature :</h2><br/> <i><tt>{sig}</tt></i></div><hr>
                <div><h2>Description : </h2><code style='display:block;white-space:pre-wrap'>{doc}</code></div><hr>
                <div>
                    <h2>Generated Code</h2>
                    Code auto-generated to use as template for client if
                    you don't want to code the exchanges yourserlf...
                    <details>
                        <summary><h3>Python Client</h3></summary>
                        <i><code style='display:block;white-space:pre-wrap'>{
            generate_python(fname, sig, doc, 'localhost', self.port)
            }</code></i>
                        <br/>Remeber, all arguments are now nammed...
                    </details>
                    <details>
                        <summary><h3>Javascrit</h3></summary>
                        <i><code style='display:block;white-space:pre-wrap'>{
            generate_js(fname, list(inspect.signature(fun).parameters.keys()), 'localhost', self.port)
            }</code></i>
                        <br/>Remember to use <tt>await</tt>...
                    </details>
                </div>
                <div style="position:absolute;bottom:5;right:5;">
                <hr><footer>Auto generated by
                ★ <a href='https://github.com/VieVie31/bonapity'>bonAPIty</a> ★
                </footer></div>
            """
            send_header(self, 200, 'text/html')
            self.wfile.write(html_out.encode())
            return

        # Check if the function the user want to call exists
        if parsed_url.path not in DecoratedFunctions.all.keys():
            send_header(self, 404, 'text/html')
            self.wfile.write(
                f"{parsed_url.path} : this function do not exists...".encode())
            return

        # Will be replaced by True id data loaded from pickle
        value_already_evaluated = False

        urlargs = parsed_url.query.split('&')
        if len(urlargs) == 1 and urlargs[0].endswith('=' * urlargs[0].count('=')) and urlargs[0] != '':
            # Only an argument without value ?  `?Ym9uYXBpdHk=`
            # this should be a base64 pickled object
            try:
                parameters = base64.b64decode(urlargs[0])
                parameters = pickle.loads(parameters)
                if type(parameters) != dict or set(map(lambda k: type(k), parameters)) != {str}:
                    send_header(self, 500, 'text/html')
                    self.wfile.write(
                        b"""
                        The encoded pickled object should be a dict (key: str, value)
                        with the name of argument as key and the corresponding
                        data as value, all keys should be strings...
                        """
                    )
                    return
                # Prepare parameters to be in the same format as
                # if processed by url : `{"key": [value(s)], ...}`
                parameters = {k: [parameters[k]] for k in parameters}
                value_already_evaluated = True
            except Exception as e:
                send_header(self, 500, 'text/html')
                self.wfile.write(str(e).encode())
                return
        else:
            # Regular way to pass data : `?arg1=val1&arg2=val2&...`
            parameters = urllib.parse.parse_qs(
                parsed_url.query
            )

        self.process(parameters, value_already_evaluated)
        return

    def do_POST(self):
        content_len = int(self.headers['Content-Length'])
        rfile = self.rfile
        if self.headers['Content-Type'] == "application/json":
            try:
                parameters = json.loads(rfile.read(content_len).decode())
            except:
                send_header(self, 400, 'text/html')
                self.wfile.write(
                    b"""Content-Type : application/json expect json object...
                    we failed to load it, check your input...
                    """
                )
        elif self.headers['Content-Type'] == "application/python-pickle":
            try:
                parameters = pickle.loads(rfile.read(content_len))
            except:
                send_header(self, 400, 'text/html')
                self.wfile.write(
                    b"""Content type : application/python-pickle expect pickle binary object...
                    we failed to load it, check your input...
                    (maybe wrong version of pickle), we use python3...")
                    """
                )
        else:
            send_header(self, 400, 'text/html')
            self.wfile.write(
                f"""Bad Content-Type : {self.headers['Content-Type']},
                accepted CT are : application/json, application/python-pickle.
                """.encode())
            return
        # TODO: handle application/x-www-form-urlencoded ?
        # print(parameters)

        # Prepare paramters in the formats as if they was parsed from url
        parameters = {k: [parameters[k]] for k in parameters}

        self.process(parameters, value_already_evaluated=True)
        return

    def do_DELETE(self):
        self.do_GET()

    def do_PUT(self):
        self.do_POST()

    def do_PATCH(self):
        self.do_POST()


class ThreadingBonAppServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    This class will make the server multi-threaded,
    allowing him to execute simulatneoulsy several client requests.
    """
    pass
