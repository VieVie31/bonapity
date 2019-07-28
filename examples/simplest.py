from bonapity import bonapity


@bonapity
def add(a: int, b: int=0) -> int:
    """Add `a` with `b`if `b`provided else return `a` only.

    Example:
    ------------------
    >>> add(4, 5)
    9
    """
    return a + b


@bonapity("hello")
def g():
    "This function return a JSON string"
    return "Like we say in french : 'Bon Appetit !'"

# without decorator this function is _private_ 
# (not accessible via the api)
def function_wo_api():
    return 23

if __name__ == "__main__":
    port = 8888
    print(f"""
    ★ Bravo ! Bravissimo ! Your first API is running ! ★
    ----------------------------------------------------

    - list functions : http://localhost:{port}/help/ 
    - display the hello world message : http://localhost:{port}/hello
    - test the `add` function : http://localhost:{port}/add?a=1&b=3
    - look at the doc of the `add` function : http://localhost:{port}/help/add

    * Try to give only the `a` parameter (`b` is default) 
      then only `b` then an extra parameter
    * Try to give non `int` parameters

    Cool ! You did it ! Now read the doc and enjoy ! :)
    """)
    bonapity.serve(port=port)
    


