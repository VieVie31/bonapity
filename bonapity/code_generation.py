"""
This module contains all stuffs about the automatic code generation.

@author: VieVie31
"""
import inspect
import hashlib
import functools

from typing import List

from .decoration_classes import DecoratedFunctions

@functools.lru_cache(maxsize=1) # Build the lib once the cache it
def generate_js_lib(domain: str, port: int, js_lib_name: str = "bonapity_api") -> str:
    # Generate the name for the requestCORS method such as there'll 
    # be no conflit with any other name of the user lib.
    requestCORS_fname =  '_' + hashlib.sha1(b'requestCORS').hexdigest()[:8]
    all_fnames = list(map(lambda fname: fname[1:], DecoratedFunctions.all))
    salt = 0
    while requestCORS_fname in all_fnames:
        requestCORS_fname = '_' + hashlib.sha1(
            (''.join(all_fnames) + str(salt)).encode()
        ).hexdigest()[:8]
        salt += 1
    # This function will do all the AJAX and w'll be used by all the others
    requestCORS_function = """
        async """ + requestCORS_fname + """(method, url, data={}) {
            var xhr = new XMLHttpRequest();
            return new Promise(function(resolve, reject) {
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                    if (xhr.status >= 300)
                    reject('[' + xhr.status + '] : ' + xhr.statusText);
                    else
                    resolve(JSON.parse(xhr.responseText));
                }
                }
                xhr.open(method, url, true);
                xhr.withCredentials = true;
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(data));
            });
        }
    """
    # Adding attributes for the domain name 
    # and the port and generating all functions
    out_lib = f""" let {js_lib_name} = {{ 
        {requestCORS_function}, 
        domain: "{domain}",
        port: {port},
        {(',' + chr(10)).join([
            f'''
            async {fname[1:]}({', '.join(inspect.signature(fun.fun).parameters.keys())}) {{
                keys = [{', '.join(map(lambda x: f'"{x}"', inspect.signature(fun.fun).parameters.keys()))}];
                if (arguments.length > keys.length)
                    throw new Exception('Too many arguments...');
                params = {{}};
                for (var i = 0; i < arguments.length; i++)
                    params[keys[i]] = arguments[i];
                url = 'http://' + this.domain + ':' + this.port + '/{fname[1:]}';
                return await this.{requestCORS_fname}('POST', url, params);
            }}
            '''
            for fname, fun in DecoratedFunctions.all.items()
        ])}
        
        }};"""
    return out_lib


def generate_js(fname: str, pnames: List[str], domain: str, port: int) -> str:
    fname = fname[1:]  # remove the starting '/'
    return f"""
    // Prefer include 'http://{domain}:{port}/help/?lib=js' in your project than C^C-C^V this code...
    async function {fname}({', '.join(pnames)}) {{
    \tkeys = [{', '.join(map(lambda x: f'"{x}"', pnames))}];
    \tif (arguments.length > keys.length)
    \t\tthrow new Exception('Too many arguments...');
    \tparams = {{}};
    \tfor (var i = 0; i < arguments.length; i++)
    \t\tparams[keys[i]] = arguments[i];
    \tparams = JSON.stringify(params);
    \turl = 'http://{domain}:{port}/{fname}';
    \tconst r = await fetch(url, {{
    \t\tmethod: 'POST',
    \t\theaders: {{
    \t\t\t'Accept': 'application/json',
    \t\t\t'Content-Type': 'application/json'
    \t\t}},
    \t\tbody: params
    \t}});
    \treturn await r.json();
    }}""".replace("    ", '')


def generate_python(fname: str, signature: str, doc: str, domain: str, port: int) -> str:
    # doc = '' #f"""'''{doc.replace("'''", '"' * 3)}\'\'\'"""
    # Replace the default function name in the signature...
    signature = '('.join([fname[1:]] + signature.split('(')[1:])
    return f"""
    from bonapity import vuosi

    @vuosi('{str(domain)}', {port})
    def {signature}:\n\tpass
    """.replace("    ", '')
