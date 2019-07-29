# 👀 README 👀

`bonAPIty` is a python3 package allowing you to create simple API (GET) 
for your functions without writting any complicated line of server code
and it's even simpler than Flask !

You are the 👨‍🍳, just do what you do the best : cook code !
don't loose your time to 💁, we do it for you... :)

By type hinting your code we cast the received inputs to the right type ! so don't worry about it... 😀

## Install

Install it with `pip3 install bonapity` and take a look to `examples/` !

## Current support

Send your data via GET and receive results in JSON.
We accept basic python data types such as : 
`int, float, bool, list, tuple, dict, set, frozenset`


For each function, your API will return your computation as JSON 
if your return type is JSON serializable or in pickle else 
(for example numpy.ndarray are not JSON serializable and 
will be returned as a binary pickle dump).


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

## In Development

> "I'll probably will do it, maybe definitely"

- `GET` api will return serialized pickle object if return type is not JSON serialisable
- `POST` api allowing you to pass non generic python types such as `numpy.ndarrays`


## License [CC-BY](https://creativecommons.org/licenses/by/4.0/)

### You are free to:

 - **Share** — copy and redistribute the material in any medium or format
 - **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms:

 - **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

 - **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
