# mathtools.py
# -- Import packages --
import math
from ._utils import _gcd_two as gcd_two
from ._functools import _cache as cache

# -- Get n-th prime --
@cache
def _nprime(n: int=1) -> int:
    # Sieve of Eratosthenes
    if n < 0:
        raise ValueError("n must be at least 0")
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 2
    if n == 3:
        return 3
    n -= 1

    # Sieve of Eratosthenes
    @cache
    def sieve_of_eratosthenes(limit) -> list:
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for start in range(2, int(limit ** 0.5) + 1):
            if sieve[start]:
                for i in range(start * start, limit + 1, start):
                    sieve[i] = False
        return [num for num, is_prime in enumerate(sieve) if is_prime]
    limit = int(n * math.log(n) * 1.2)
    while True:
        primes = sieve_of_eratosthenes(limit)
        if len(primes) >= n:
            return primes[n - 1]
        limit *= 2

# -- Check if a number is prime --
@cache
def _isprime(n: int=1) -> bool:
    if n < 1:
        return False
    if n == 1 or n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0 or n % 4 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# -- Check if a number is a power of another number --
@cache
def _is_power(xx: int, x: int) -> bool:
    return xx % x == 0

# -- Check if a number is a perfect square --
@cache
def _is_perfect_square(n: int) -> bool:
    return _is_power(n, 2)

# -  Pythagorean theorem --
@cache
def _pythagorean(a: float|int=None, b: float|int=None, c: float|int=None) -> float|int:
    if sum(x is not None for x in (a, b, c)) != 2:
        raise ValueError("Exactly two arguments must be provided")
    if any(x is not None and (not isinstance(x, (int, float)) or x < 0) for x in (a, b, c)):
        raise ValueError("Arguments must be non-negative numbers")
    if c is None:
        return math.sqrt(a**2 + b**2)
    if a is None:
        if c <= b:
            raise ValueError("Hypotenuse must be greater than leg")
        return math.sqrt(c**2 - b**2)
    if b is None:
        if c <= a:
            raise ValueError("Hypotenuse must be greater than leg")
        return math.sqrt(c**2 - a**2)
    raise ValueError("Invalid combination of arguments")

# -- Get the n-th Fibonacci number --
@cache
def _fib(n: int=1) -> int:
    ans = [0, 1]
    for i in range(2, n + 1):
        ans.append(ans[i - 1] + ans[i - 2])
    return ans[n]

# -- Check if the given number is a Fibonacci number and return bool --
@cache
def _checkfib(x: int=1, return_nearest: bool=False) -> bool|int:
    if not isinstance(x, int) or x < 0:
        return (False, 0) if return_nearest else False
    is_fib = _is_perfect_square(5 * x * x + 4) or _is_perfect_square(5 * x * x - 4)
    if not return_nearest:
        return is_fib
    # Find nearest Fibonacci number
    a, b = 0, 1
    while b < x:
        a, b = b, a + b
    nearest = b if abs(b - x) < abs(a - x) else a
    return is_fib, nearest

# -- Factorize a number into its prime factors --
@cache
def _factorize(n: int) -> list:
    factors = []
    i = 2
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 1
    if n > 1:
        factors.append(n)
    return factors

# -- Greatest Common Divisor (GCD) for multiple numbers --
@cache
def _gcd(*args: int) -> int:
    if len(args) < 2:
        raise ValueError("At least two numbers are required")
    if not all(isinstance(x, int) for x in args):
        raise TypeError("All inputs must be integers")
    if not all(x > 0 for x in args):
        raise ValueError("All inputs must be positive integers")
    
    result = args[0]
    for num in args[1:]:
        result = gcd_two(result, num)
    return result

# -- Least Common Multiple (LCM) for multiple numbers --
@cache
def _lcm(*args: int) -> int:
    if len(args) < 2:
        raise ValueError("At least two numbers are required")
    if not all(isinstance(x, int) for x in args):
        raise TypeError("All inputs must be integers")
    if not all(x > 0 for x in args):
        raise ValueError("All inputs must be positive integers")
    
    def lcm_two(a: int, b: int) -> int:
        return abs(a * b) // gcd_two(a, b)
    
    result = args[0]
    for num in args[1:]:
        result = lcm_two(result, num)
    return result

# -  Find all divisors of a number --
@cache
def _divisors(n: int) -> list:
    return [i for i in range(1, n + 1) if n % i == 0]

# -- Check if a number is a perfect number --
@cache
def _is_perfect_number(n: int) -> bool:
    return sum(_divisors(n)) == 2 * n

# -- Compute the sum of the digits of a number --
@cache
def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))

# -- Compute the factorial of a number --
@cache
def _factorial(n: int) -> int:
    if not isinstance(n, int):
        raise TypeError("Input must be an integer.")
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# -- Compute the binomial coefficient nCr --
@cache
def _ncr(n: int, r: int) -> int:
    if not (0 <= r <= n):
        raise ValueError("r must be between 0 and n inclusive")
    return _factorial(n) // (_factorial(r) * _factorial(n - r))

# -- Compute the mean of a list of numbers --
@cache
def _mean(*numbers):
    total = sum(numbers)
    count = len(numbers)
    if count == 0:
        return 0.0
    return total / count

# -- Compute the median of a list of numbers --
@cache
def _median(*numbers):
    if not numbers:
        return 0.0
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    
    if n % 2 == 1:
        return float(sorted_numbers[n // 2])
    else:
        mid1 = sorted_numbers[n // 2 - 1]
        mid2 = sorted_numbers[n // 2]
        return (float(mid1) + float(mid2)) / 2.0