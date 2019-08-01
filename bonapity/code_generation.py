"""
This module contains all stuffs about the automatic code generation.

@author: VieVie31
"""
from typing import List


def generate_js(fname: str, pnames: List[str], domain: str, port: int) -> str:
    fname = fname[1:]  # remove the starting '/'
    return f"""
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


