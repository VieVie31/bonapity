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
import http.cookies
import urllib.parse
import urllib.request
import socketserver
import os.path
import threading
import queue
import contextvars

from pathlib import Path
from copy import deepcopy
from collections import defaultdict

from .code_generation import generate_js, generate_python, generate_js_lib
from .decoration_classes import DecoratedFunctions
from .mime import extension_to_mime, byte_to_mime
from .html_generation import make_html_index, make_html_function_doc
from .session import SessionManager, make_session_id


def send_header(server_instance, code, content_type, cookies=None):#, session_id=None):
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

    # Send regular cookies
    if cookies != None:
        server_instance.send_header('Set-Cookie', cookies.output(header='', sep=';\r\nSet-Cookie: '))

    session_id = server_instance.get_cookies_and_session_id()[1]

    server_instance.send_header("Access-Control-Allow-Credentials", 'true')
    server_instance.send_header('Set-Cookie', f'BONAPITYSID={session_id if session_id else make_session_id()}')
    server_instance.end_headers()


class BonAppServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kargs):
        super(BonAppServer, self).__init__(*args, **kargs)
        self.help = True
        self.port = 80
        self.default_timeout = 1
        self.static_files_dir = None
        self.index = None
        self.bonapity = None

    def get_cookies_and_session_id(self):
        cookies = self.headers.get('Cookie')
        cookies = http.cookies.SimpleCookie(cookies)
        cookies = deepcopy(cookies)

        # BONAPITYSID is the reserved cookie name for sessions
        if "BONAPITYSID" in cookies:
            # Get the session id
            session_id = cookies["BONAPITYSID"].value
            # Do not allow modification of the cookie session, pop it
            cookies.pop("BONAPITYSID")
        else:
            session_id = make_session_id()
        return cookies, session_id

    def process(self, parameters, value_already_evaluated=False):
        """
        This method do the common stuffs between do_GET and do_POST.

        :param parameters: key-value dict of parameters (values are not parsed)
        """
        cookies, session_id = self.get_cookies_and_session_id()
        # Get the session
        session = SessionManager()[session_id]

        parsed_url = urllib.parse.urlparse(self.path)

        decorated_function = DecoratedFunctions.all[parsed_url.path]

        # Get the function in the decorated function list
        fun = decorated_function.fun
        sig = inspect.signature(fun)

        # Get the timeout informatin of the function, is None set a default one
        timeout = decorated_function.timeout
        if timeout is None:
            timeout = self.default_timeout

        # Get mime-type
        mime_type = decorated_function.mime_type

        # Check if parameters names matches
        # (and ignore default and *args, **kargs parameters)
        full_arg_spec = inspect.getfullargspec(fun)
        ignored_params_names = [
            k for k in sig.parameters.keys()
            if sig.parameters[k].default != inspect._empty
               or k == full_arg_spec.varargs
               or k == full_arg_spec.varkw
        ]

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
            if full_arg_spec.varargs is not None \
                and len(full_arg_spec.varargs):
                f = functools.partial(f, *parameters[full_arg_spec.varargs])

            # Fill the **kargs if any
            if full_arg_spec.varkw is not None \
                    and isinstance(parameters[full_arg_spec.varkw], dict) \
                    and len(full_arg_spec.varkw):
                f = functools.partial(f, **parameters[full_arg_spec.varkw])


            # Prepare the function to be executed within a context
            # Needed to resolve the contextvariables
            orig_f = f # Copy in another name to avoid infinite recursion
            f = lambda: self.bonapity._BonAPIty__exec_function(orig_f, cookies, session)

            if timeout > 0.:
                que = queue.Queue()
                thr = threading.Thread(target=lambda q: q.put(f()), args=(que,))
                thr.start()
                thr.join(timeout)

                # TODO: differentiate timeout form function crash

                if que.empty():
                    # Time out error
                    send_header(self, 500, 'text/html')
                    self.wfile.write(
                        f"""Timeout error: execution of {fun.__name__}
                        took more than the {timeout} allowed seconds
                        or function crashed... (see server logs)
                        """.encode()
                    )
                    return
                else:
                    # Get result from the top of the queue
                    res, cookies = que.get()
            else:
                # No timeout constraint
                res, cookies = f()

            # If a mime-type is given, return as is (byte data assumed)
            if mime_type not in [None, "auto"]:
                # Check if data is in byte format
                if type(res) != type(b''):
                    send_header(self, 500, 'text/html')
                    self.wfile.write(
                        f"{fun.__name__} didn't returned byte data but :{str(res)[:100]}...".encode())
                    return
                # The data are bytes
                send_header(self, 200, str(mime_type), cookies=cookies)
                self.wfile.write(res)
                return
            elif mime_type in [None, "auto"] and type(res) == type(b''):
                suffix = Path(parsed_url.path).suffix
                if suffix:
                    # If extension provided in file name detect from if
                    mime_type = extension_to_mime(suffix)
                else:
                    # Try to infer mine-type from 16 first bytes (enought)
                    # else return "application/octet-stream"
                    mime_type = byte_to_mime(res[:16])
                    # raise NotImplementedError()
                # The data are bytes
                send_header(self, 200, str(mime_type), cookies=cookies)
                self.wfile.write(res)
                return

            # Ecode result in JSON
            try:
                res = json.dumps(res, cls=decorated_function.json_encoder)

                # Send success
                send_header(self, 200, 'application/json', cookies=cookies)
                self.wfile.write(
                    f"{res}".encode()
                )
                return
            except Exception as e:
                # Encore into pickle and send a binary object
                try:
                    res = pickle.dumps(res)

                    # Send success
                    send_header(self, 200, 'application/python-pickle', cookies=cookies)
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

    def __return_file(self, file_path, mime_type: str = None):
        """Serve a given file from a `path_file` and
        detect `mime_type` if not provided
        """
        # Serve the file
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                if mime_type is None: 
                    # Detect mime_type if `None`
                    mime_type = extension_to_mime(Path(file_path).suffix)
                    if mime_type == 'application/octet-stream':
                        # Try to determine mime from 16 first bytes
                        mime_type = byte_to_mime(data[:16])
                send_header(self, 200, mime_type)
                self.wfile.write(data)
                return
        except Exception as e:
            send_header(self, 500, 'text/html')
            self.wfile.write(
                f"Error in serving file {file_path}: {e}".encode())
            return

    def __return_help_page(self, parsed_url):
        "Return an html help index page or the help of a given function"
        fname = parsed_url.path[5:]

        # If no name given, make an index of all functions allowed in the API
        if fname in ['', '/', '/*']:
            modules = defaultdict(list)
            for fname in DecoratedFunctions.all.keys():
                modules[DecoratedFunctions.all[fname].fun.__module__].append(fname)

            html_out = make_html_index(modules)

            send_header(self, 200, 'text/html')
            self.wfile.write(html_out.encode())
            return
        elif not self.help and parsed_url.path == '/':
            send_header(self, 404, 'text/html')
            self.wfile.write(b'')
            return

        #FIXME: to allow regex
        elif fname not in DecoratedFunctions.all.keys():
            send_header(self, 404, 'text/html')
            self.wfile.write(
                f"{fname} : this function do not exists...".encode())
            return
        fun = DecoratedFunctions.all[fname].fun
        sig = html.escape(f"{fun.__name__}{inspect.signature(fun)}")
        doc = html.escape(fun.__doc__) if fun.__doc__ else ''

        # Extract domain, port from the client request (socket)
        domain, port = self.request.getsockname()

        html_out = make_html_function_doc(
            fname, sig, doc, 
            generate_python(fname, sig, doc, domain, port), 
            generate_js(fname, list(inspect.signature(fun).parameters.keys()), domain, port)
        )

        send_header(self, 200, 'text/html')
        self.wfile.write(html_out.encode())
        return
    
    def __extract_parameters_from_url(self, parsed_url):
        """Return the parameters extracted from the `parsed_url`
        as urlargs or base64 pickle and return a boolean indicating
        if the variables have been evaluated (True for pickle).
        This should be passed to the process method.

        :return: parameters as dict, boolean
        """
        # Will be replaced by True if data loaded from pickle
        value_already_evaluated = False

        urlargs = parsed_url.query.split('&')
        if len(urlargs) == 1 and urlargs[0].endswith('=' * urlargs[0].count('=')) and urlargs[0] != '':
            # Only an argument without value ?  `?Ym9uYXBpdHk=`
            # this should be a base64 pickled object
            try:
                parameters = base64.b64decode(urlargs[0])
                parameters = pickle.loads(parameters)
                if type(parameters) != dict or set(map(type, parameters)) != {str}:
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

        return parameters, value_already_evaluated

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)

        # Serve the index page if exists else display an error
        if self.index and parsed_url.path in ['', '/']:
            self.__return_file(self.index, 'text/html')
            return
        # Check to display the js lib
        elif self.help and parsed_url.path.startswith('/help/') and parsed_url.query in ['lib=js', 'js']:
            send_header(self, 200, 'text/javascript')
            self.wfile.write(generate_js_lib(*self.request.getsockname()).encode())
            return
        # Check if display help
        elif self.help and (parsed_url.path.startswith('/help/') or parsed_url.path in ['', '/']):
            self.__return_help_page(parsed_url)
            return

        # If the function the user want to call do not exists
        # check if a file exists from the root `static_files_dir`
        #TODO: split the `?` and `#` ?
        file_path = (Path(self.static_files_dir) / Path(parsed_url.path[1:])).absolute()
        if parsed_url.path not in DecoratedFunctions.all.keys() and os.path.isfile(file_path):
            self.__return_file(file_path)
            return

        #FIXME: to allow regex
        elif parsed_url.path not in DecoratedFunctions.all.keys():
            send_header(self, 404, 'text/html')
            self.wfile.write(
                f"{parsed_url.path} : this function do not exists...".encode())
            return

        parameters, value_already_evaluated = self.__extract_parameters_from_url(parsed_url)

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
