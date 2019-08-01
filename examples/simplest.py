from bonapity import bonapity


@bonapity
def add(a: int, b: int = 0) -> int:
    """ Add `a` with `b` if `b` is provided, otherwise returns `a` only.

    Example:
    ------------------
    >>> add(4, 5)
    9
    """
    return a + b


@bonapity
def concatenate(s1: str, s2: str) -> str:
    """ Return the concatenation of `s1` with `s2`. """
    return s1 + s2


# Note that the decorator can be used to change the name of the served API.
@bonapity("hello")
def g():
    """ This function returns a fixed string. """
    return "Like we say in french : 'Bon Appétit !'"


# Without decorator this function is _private_ (not accessible via the API).
def function_wo_api():
    return 23


@bonapity(timeout=6)
def wait(s: int=1) -> int:
    """
    The purpose of this function is only to show that 
    the miltithreading is supported by your API server ! :D

    Go to your terminal and write:
    ```bash
    for i in 1 2 3 4 5; 
    do
        curl "http://localhost:8888/wait?s=5" & 
    done
    ```
    All the  5 should be printed at the same time just after 5 seconds 
    and not one after the other which would take instead : 5s * 5s = 25s 
    before printing the last one.

    :param s: the number of seconds before returning its value `s`
    :return: `s` the number of seconds asked to wait
    """
    import time
    time.sleep(s)
    return s


if __name__ == "__main__":
    port = 8888
    print(f"""
    ★ Bravo ! Bravissimo ! Your first API is running ! ★
    ----------------------------------------------------

    - list functions : http://localhost:{port}/help/ 
    - display the hello world message : http://localhost:{port}/hello
    - test the `add` function : http://localhost:{port}/add?a=1&b=3
    - look at the doc of the `add` function : http://localhost:{port}/help/add
    - try the `concatenate` function : http://localhost:{port}/concatenate?s1=3&s2=4
    - test the `wait` function : http://localhost:{port}/wait?s=4

    * Try to give only the `a` parameter (`b` is default) 
      then only `b` then an extra parameter
    * Try to give non `int` parameters
    * Try ti delete the specific `timeout` parameter in the wait function
    * Hack this file :)

    Cool ! You did it ! Now read the doc and enjoy ! :)
    """)
    bonapity.serve(port=port, timeout=10) #by default, every function will stop after 10s execution completed or not
