
import numpy as np


# refer: https://stackoverflow.com/a/38194669/14791867
def conv(u: np.array = [], v: np.array = []) -> np.array:
    return np.convolve(u, v, 'full')
