"""Test utility functions."""

import numpy as np
import numpy.typing as npt


def conjugate_if(array: npt.NDArray, conjugate: bool) -> npt.NDArray:
    """Return the complex conjugate if conjugate is True."""
    return np.conjugate(array) if conjugate else array


def create_array(rng: np.random.Generator, size: tuple[int, int], dtype: str, order: str) -> npt.NDArray:
    """Create an array with the specified size, dtype, and memory order."""
    array = np.empty(size, dtype=dtype, order=order)
    if np.isrealobj(array):
        array[:] = rng.uniform(low=-1.0, high=1.0, size=size)
    else:
        array.real = rng.uniform(low=-1.0, high=1.0, size=size)
        array.imag = rng.uniform(low=-1.0, high=1.0, size=size)
    return array


def create_symmetric_array(
    rng: np.random.Generator, upper: True, size: int, dtype: str, order: str
) -> tuple[npt.NDArray, npt.NDArray]:
    """Create a symmetric array with the specified size, dtype, and memory order."""
    mat_a = np.empty((size, size), dtype=dtype, order=order)
    mat_a_full = np.empty((size, size), dtype=dtype, order=order)
    if upper:
        for i in range(size):
            for j in range(i, size):
                mat_a[i, j] = rng.random(size=1, dtype=dtype)[0]
                mat_a_full[i, j] = mat_a[i, j]
        for i in range(size):
            for j in range(i):
                mat_a[i, j] = np.nan
                mat_a_full[i, j] = mat_a[j, i]
    else:
        for i in range(size):
            for j in range(i + 1):
                mat_a[i, j] = rng.random(size=1, dtype=dtype)[0]
                mat_a_full[i, j] = mat_a[i, j]
        for i in range(size):
            for j in range(i + 1, size):
                mat_a[i, j] = np.nan
                mat_a_full[i, j] = mat_a[j, i]
    return mat_a, mat_a_full
