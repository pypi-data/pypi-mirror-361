"""
test_sampler.py — Functional test and performance benchmark for sample_balanced.

Includes:
- test_sample_balanced_shape_and_balance(): correctness unit test
- main(): benchmark timing for large-scale simulations
"""

import time

import numpy as np
from sampleplan import sample_balanced


def test_sample_balanced_shape_and_balance():
    """Verify shape and balance properties for small inputs."""
    symbols = ['a', 'b', 'c']
    size = 100
    m = 3
    seed = 123

    seq = sample_balanced(symbols, m=m, size=size, seed=seed)

    assert seq.shape == (size, len(symbols) * m), \
        f"Expected shape {(size, len(symbols) * m)}, got {seq.shape}"

    expected = sorted(symbols * m)
    for i, row in enumerate(seq):
        assert sorted(row.tolist()) == expected, f"Row {i} not balanced"


def main():
    """Run a high-volume benchmark to test runtime performance."""
    symbols = ['a', 'b', 'c']
    size = 1_000_000
    m = 3
    seed = 42

    print(f"Testing {size:,} simulations with m={m}, seed={seed}...")

    start = time.time()
    seq = sample_balanced(symbols=symbols, m=m, size=size, seed=seed)
    duration = time.time() - start

    assert seq.shape == (size, len(symbols) * m), "Shape mismatch"
    assert sorted(seq[0].tolist()) == sorted(symbols * m), "First row not balanced"

    print(f"First 3 rows:\n{seq[:3]}")
    print(f"Took {duration:.4f} sec for {size:,} items")


if __name__ == "__main__":
    main()
