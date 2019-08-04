# 👀 README 👀

`bonAPIty` is a python (3.7) ackage allowing you to create simple API (REST) for your functions without writing any complicated line of server code and it is much simpler than Flask !  

You are the 👨‍🍳, just do what you do the best: cook code ! Do not lose your time to 💁, we do it for you :).  

By type hinting your code we cast the received inputs to the right type, so do not worry about it 😀.

## Install

> "See, unlike most hackers, I get little joy out of figuring out how to install the latest toy."
>
> -- <cite>Jamie Zawinski</cite>

Install it with `pip3 install bonapity` and take a look at `examples/` !

## Current support

Your API is REST compliant (accept the following verbs : `GET`, `POST`, `PUT`, `PATCH`, `DELETE`) !

For each function, your API will return your computation as a JSON object if your return type is JSON serializable, or in the pickle format otherwise. For example, numpy.ndarray objects are not JSON serializable and will be returned as a binary pickle dump.

If you want to learn more about how it's working, take a loot to the "_How To_" section.

## Example

> "I think the greatest way to learn is to learn by someone's example."
>
> -- <cite>Tobey Maguire</cite>

### Writting your first API

```python
from bonapity import bonapity

@bonapity
def add(a: int, b: int) -> int:
    """ Add two numbers. """
    return a + b

if __name__ == "__main__":
    bonapity.serve(port=8888)
```

### Requesting your first API

Testing REST verbs requests with `curl` :

```bash
curl -X GET "http://localhost:8888/add?a=1&b=3"
curl -X DELETE "http://localhost:8888/add?a=1&b=3"
curl --data '{"a": 1, "b": 3}' -X POST   "http://localhost:8888/add" -H "Content-Type: application/json"
curl --data '{"a": 1, "b": 3}' -X PATCH  "http://localhost:8888/add" -H "Content-Type: application/json"
curl --data '{"a": 1, "b": 3}' -X PUT    "http://localhost:8888/add" -H "Content-Type: application/json"
```

### Looking your first generated API function documentation

Generated documentation for your first function is available at this url : `http://localhost:8888/help/add`.

### More Examples

For more examples with explanations take a look to the `examples/` dir.  
Recommended order for reading :

- How to import the decorator, use it and serve : `simplest.py`.
- Having a simple web interface using your simplest.py API : `simplest.html`.
- Using your API from a python client : `np_server_api.py`, `np_client_api.py`.
- Send/receive complex non python generic data types (such as np.ndarray) with a python client : `python_server.py`, `python_client.py`.

## How To

> "I am not accustomed to protocol."
>
> -- <cite>Evo Morales</cite>

We currently support 2 kinds of requests : `GET`, `DELETE` vs. `POST`, `PUT`, `PATCH`.
Each of them accept 2 different ways to get your data/parameters sent from the client to the your API.

But remember, we process those encoded data and present them to your code as if
they were not received from a complex protocol, everything is transparent for you !

You don't need to read this section for a quick start, just use the generated
wrappers in the generated documentation of your API (run the server and go to `/help/`), read this only if you want to get your hands dirty and not use the
generated wrapper but write your one instead.

### GET, DELETE

- **query string** : `/myfun?param1=value1&param2=value2`.  
   Each value can be formatted in JSON or a python string (eg. `v=True`is python but will be interpreted as the boolean `True` as if `v=true` which is the JSON encoding). Note that if your value is a string, it should be surrounded by `"`.
- **pass pickle object** : `/myfun?MY_BASE64_ENCODED_DATA`. 
   You can pass complex non JSON serializable python type by encoding in base64 the binary pickle dump representation of your data.  
   Here the encoded data should be a key/value dictionary where keys correspond to the parameters name of your function and values are... well your values.  
   This argument SHOULD NOT have a value !  
   For example, the equivalent of `/myfun?v=23` would be `/myfun?gAN9cQBYAQAAAHZxAUsXcy4=` because `gAN9cQBYAQAAAHZxAUsXcy4=` the base64 of `\x80\x03}q\x00X\x01\x00\x00\x00vq\x01K\x17s.` which is the pickle dump of `{'v': 23}`.  
   Note that we use python3, do not encode in the python2 version of pickle.

### POST, PUT, PATCH

- **application/json** :
   The data received by the server will be parsed as a JSON file and interpreted as a key/value dictionary where keys correspond to your param names of your functions and values the corresponding values.  
   Here the encoded data should be a key/value dictionary where keys correspond to the parameters name of your function and values are... well your values.
- **application/python-pickle** :
   The data received should be a binary pickled object (do not encode it in base64 for example) which will be loaded by pickle (python3, be aware of your pickle encoder version).
- No other type of content is accepted (such as _application/x-www-form-urlencoded_), so, if you are using the `requests` module, be aware to not write `requests.post(url, data={...})` but `requests.post(url, json={...})` instead, or specifying the _Content-Type_ in the header.

## Goodies

By default, each served function will have an documentation page automatically build from your doctring and the signature of the function available at `http:/domain:port/help/myfunction`.

Furthermore, to make your life easier when writting a JS client, we automatically generate wrapper of all your function into a single JS script you can include from this address: `http://domain:port/help/?js`. The generation is quite naïve and just an help, if you encounter difficulties with the generated lib, consider to writte wrappers for your spetial use cases your self.


## In Development

> "I'll probably will do it, maybe definitely"
>
> -- <cite>Donald J. Trump</cite>

- [x] `POST` support
- [x] returning serialized pickle dump if return type is not JSON serializable
- [x] allow to pass non generic python types such as `numpy.ndarrays` as parameter
- [x] add automatic wrapper code generation to include in doc (will make usage by clients even much simpler) (TODO: make a better python version not converting the args into kargs)
- [x] Handle the others commands of the REST API standard : `PUT`, `DELETE`, `PATCH`
- [x] make the server multi-threaded to be non blocking (non sequential, request after request)
- [x] allow to put time limit execution on function to not be f*** by infinite loop or just too long function coupled with stupid/poorly intensionned user
- [ ] add Session support
- [x] generate wrappers of all the functions available in API into a served JavaScript file to just have to include the link (`http://localhost:8888/help/?js`)
- [x] rewrite code-generation for javascript as `fetch` do not handle cookies
- [ ] Travis testing
- [ ] Complete documentation and publish on a website


## License [CC-BY](https://creativecommons.org/licenses/by/4.0/)

> "We protect monopolies with copyright."
>
> -- <cite>Peter Thiel</cite>

### You are free to

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.
The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
