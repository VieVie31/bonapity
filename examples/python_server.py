import numpy as np

from bonapity import bonapity

@bonapity
def reshape(ndarray, nrow, ncol):
    return ndarray.reshape(nrow, ncol)

if __name__ == "__main__":
    bonapity.serve()

