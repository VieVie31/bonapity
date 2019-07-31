# 👀 README 👀

`bonAPIty` is a python3 package allowing you to create simple API (GET & POST) 
for your functions without writting any complicated line of server code
and it's even simpler than Flask !

You are the 👨‍🍳, just do what you do the best : cook code !
don't loose your time to 💁, we do it for you... :)

By type hinting your code we cast the received inputs to the right type ! so don't worry about it... 😀

## Install

Install it with `pip3 install bonapity` and take a look to `examples/` !


## Example

```python
from bonapity import bonapity

@bonapity
def add(a: int, b: int) -> int:
    "Add two numbers"
    return a + b

if __name__ == "__main__":
    bonapity.serve()
```

For more examples with explanations take a look to the `examples/` dir...

Recommanded order for reading : 

- How to import the decorator, use it and serve : `simplest.py`
- Having a simple web interface using your simplest.py API : `simplest.html`
- Using your API from a python client : `np_server_api.py`, `np_client_api.py`
- Send/receive complex non python generic data types (such as np.ndarrays) with a python client : `python_server.py`, `python_client.py`

## How To ?

> "I am not accustomed to protocol."
> 
> -- <cite>Evo Morales</cite>

We currently support 2 types of requests : `GET` and `POST`. 
Each of them accept 2 different ways to get your data/parameters transfered from client to the your API. 

But remember, we process those encoded data and present them to your code as if
they wasn't received from a complex protocol, everything is transparent for you !

You don't need to read this section for a quick start, just use the generated 
wappers in the generated documentation of your API (run the server and go to `/help/`), read this only if you want to have hands dirty and not use the 
generated wrapper but write your ones instead...

### GET
 - **query string** : `/myfun?param1=value1&param2=value2`.  
   Each value can be formated in JSON or a python string (eg. `v=True`is python but will be interpreted as the boolean `True` as if `v=true` which is the JSON encoding). Note that if your value is a string, it should be surrounded by `"`...
 - **pass pickle object** : `/myfun?MY_BASE64_ENCODED_DATA`. 
   You can pass complex non JSON serializabe python type by encoding in base64 the binary pickle dump representation of your data.  
   Here the encoded data shoud be a key/value dictionnary where keys correspond to the parameters name of your function and values are... your values...  
   This argument SHOULD NOT have a value !  
   For example, the equivalent of `/myfun?v=23` would be `/myfun?gAN9cQBYAQAAAHZxAUsXcy4=` because `gAN9cQBYAQAAAHZxAUsXcy4=` the base64 of `\x80\x03}q\x00X\x01\x00\x00\x00vq\x01K\x17s.` which is the pickle dump of `{'v': 23}`.  
   Note that we use python3, do not encode in the python2 version of pickle...

### POST
 - **application/json** : 
   The data receveid by the server will be parsed as a JSON file and interpreted as a key/value dictionary where keys correspond to your param names of your functions and values the corresponding values...  
   Here the encoded data shoud be a key/value dictionnary where keys correspond to the parameters name of your function and values are... your values...
 - **application/python-pickle** : 
   The data received should be a binary pickled object (do not encode it in base64 for example) which will be loaded by pickle (python3, be aware of your pickle encoder version).
 - No other type of content is accepted (such as _application/x-www-form-urlencoded_), so, if you are using the requests module be aware to not write `requests.post(url, data={...})` but `requests.post(url, json={...})` instead, or specifying the _Content-Type_ in the header...


## In Development

> "I'll probably will do it, maybe definitely"
> 
> -- <cite>Donald J. Trump</cite>

- [x] `POST` suppport
- [x] returning serialized pickle dump if return type is not JSON serializable
- [x] allow to pass non generic python types such as `numpy.ndarrays` as parameter
- [x] add automatic wapper code generation to include in doc (will make usage by clients even much simpler) (TODO: make a better python version not converting the args into kargs)
- [ ] Handle the others commands of the REST API standard : `PUT`, `DELETE`, `PATCH`
- [ ] make the server multithreaded to be non blocking (non sequential, request after request)


## License [CC-BY](https://creativecommons.org/licenses/by/4.0/)

> "We protect monopolies with copyright."
> 
> -- <cite>Peter Thiel</cite>

### You are free to:

 - **Share** — copy and redistribute the material in any medium or format
 - **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms:

 - **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

 - **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
