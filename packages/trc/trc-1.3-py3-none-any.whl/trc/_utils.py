# utils.py
# -- Import packages --
from ._functools import _cache as cache

# -- Helper function for GCD of two numbers --
@cache
def _gcd_two(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a