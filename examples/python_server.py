import numpy as np

from bonapity import bonapity


@bonapity
def reshape(ndarray: np.ndarray, nrow: int, ncol: int) -> np.ndarray:
    return ndarray.reshape(nrow, ncol)


if __name__ == "__main__":
    bonapity.serve()
