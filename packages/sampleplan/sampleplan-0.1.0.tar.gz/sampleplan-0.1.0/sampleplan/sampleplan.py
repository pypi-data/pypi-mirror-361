"""
sampleplan.py — Fast balanced sequence generator via compiled Nim backend.

This module provides the `sample_balanced` function, which returns randomized,
balanced sequences where each unique symbol appears the same number of times
per simulation. Ideal for simulations, randomized testing, or experimental design.

Powered by a shared library compiled from Nim and interfaced via `ctypes`.

Example
-------
>>> from sampleplan import sample_balanced
>>> sample_balanced(['A', 'B', 'C'], m=2, size=3, seed=42)
array([['B', 'C', 'B', 'C', 'A', 'A'],
       ['C', 'A', 'B', 'A', 'C', 'B'],
       ['A', 'B', 'C', 'B', 'C', 'A']], dtype='<U1')
"""

from typing import Sequence, Union
import platform
import ctypes
import os

from numpy.typing import NDArray
import numpy as np


# Determine shared library extension by OS
ext_map = {'Windows': 'dll', 'Linux': 'so', 'Darwin': 'dylib'}
ext = ext_map.get(platform.system())

if ext is None:
    raise RuntimeError(
        f"Unsupported OS: {platform.system()}. "
        "Only Windows, Linux, and macOS are currently supported."
    )

this_dir = os.path.dirname(__file__)
libname = os.path.join(this_dir, f'sampleplan.{ext}')

# Defensive load with helpful error if library is missing
if not os.path.exists(libname):
    raise ImportError(
        f"Shared library not found: {libname}. "
        "Ensure the correct DLL/SO/DYLIB is built and available in the "
        "package directory."
    )

# Load the shared Nim-compiled library
lib = ctypes.CDLL(libname)

# Define argument and return types for the shared C interface
int_ptr = ctypes.POINTER(ctypes.c_int)
lib.sampleBalanced.argtypes = [
    int_ptr,       # symbols
    ctypes.c_int,  # symbolCount
    ctypes.c_int,  # m
    ctypes.c_int,  # size
    ctypes.c_int,  # seed
    int_ptr        # outSeq
]

lib.sampleBalanced.restype = None  # void function: fills buffer in-place


def sample_balanced(
    symbols: Sequence[Union[int, str]], m: int = 1, size: int = 1,
    seed: int = -1
) -> NDArray:
    """
    Generate balanced random permutations of a list of unique symbols.

    Each row of the returned array is a shuffled sequence in which every
    symbol appears exactly `m` times. Multiple such sequences can be
    generated in parallel via the `size` argument.

    Arguments
    ---------
    symbols:
        A sequence of unique values (e.g. strings or integers).
    m:
        Number of repetitions per symbol per simulation. Must be ≥ 1.
    size:
        Number of independent simulations to generate. Must be ≥ 1.
    seed:
        Optional seed for deterministic sampling. Use -1 to ignore and sample
        randomly.

    Returns
    -------
    A NumPy array of shape `(size, len(symbols) * m)` containing shuffled,
    balanced sequences. The dtype matches the input symbol type (e.g. `str` or
    `int`).

    Raises
    ------
    ValueError:
        If symbols are empty, non-unique, or m/size are invalid.

    Example
    -------
    >>> sample_balanced(["a", "b", "c"], m=2, size=2, seed=1)
    array([
        ['b', 'c', 'a', 'c', 'b', 'a'],
        ['c', 'b', 'b', 'a', 'a', 'c']
    ])
    """
    if not symbols:
        raise ValueError("`symbols` must be a non-empty sequence.")

    if len(set(symbols)) != len(symbols):
        raise ValueError("`symbols` must contain only unique values.")

    if size < 1:
        raise ValueError(
            f"`size` must be a positive integer, got value `{size}`."
        )

    if m < 1:
        raise ValueError(
            f"`m` must be a positive integer, got value `{m}`."
        )

    symbols = np.asarray(symbols, dtype=object)
    n = len(symbols)
    symbol_ids = np.arange(n, dtype=np.int32)
    raw_result = np.empty(n * m * size, dtype=np.int32)

    lib.sampleBalanced(
        symbol_ids.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        len(symbols),
        m,
        size,
        seed,
        raw_result.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    )

    decoded = symbols[raw_result]

    # Safe reshape since output is guaranteed to be of length size × n × m
    return decoded.reshape(size, n * m)
