import numpy as np

from bonapity import vuosi

# This decorator will do the API's call for you, don't worry !
@vuosi('localhost', 8888)
# The function should have the same signature as the API
def reshape(ndarray: np.ndarray, nrow: int, ncol: int) -> np.ndarray:
    # <!> the argument are automatically transformed into key 
    # arguments take a look to the call bellow...
    pass


if __name__ == "__main__":
    print('---------------------------------------------------------------')
    print("Passing numpy array to the api and receive a numpy array too...")
    print('---------------------------------------------------------------\n')
    original = np.ones((2, 3))
    r, c = 6, 1
    print("Inputs :\n", original, '\n', r, c)
    print("\nCall to `reshape`...\n")
    # <!> all argument should be given with the argname
    res = reshape(ndarray=original, nrow=r, ncol=c)
    print("Outputs :\n", res)
    print("\nPretty cool ! no ?\n")
    print("All the complex api server calls are already done for you !\n")
    print("Just use the `@vuosi` decorator... :D\n")
    print("BonAPIty ! Merci, VuOssi ! ;)")
