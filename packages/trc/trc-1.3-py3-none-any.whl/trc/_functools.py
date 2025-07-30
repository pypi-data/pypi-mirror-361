# functools.py
# -- Import modules --
import time

# -- Cache a function result --
def _cache(func: callable) -> callable:
    cache_dict = {}

    def make_hashable(obj: any) -> any:
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        if isinstance(obj, tuple):
            return tuple(make_hashable(item) for item in obj)
        if isinstance(obj, list):
            return tuple(make_hashable(item) for item in obj)
        if isinstance(obj, set):
            return frozenset(make_hashable(item) for item in obj)
        if isinstance(obj, dict):
            return tuple(sorted((make_hashable(k), make_hashable(v)) for k, v in obj.items()))
        return str(obj)

    def wrapper(*args, **kwargs) -> any:
        key = make_hashable((args, kwargs))
        if key in cache_dict:
            return cache_dict[key]
        result = func(*args, **kwargs)
        cache_dict[key] = result
        return result

    return wrapper

# -- Measure execution time --
def _timer(func: callable) -> callable:
    # Decorator
    def wrapper(*args, **kwargs) -> tuple[float, any]:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        needed_time = end_time - start_time
        return needed_time, result
    return wrapper

# -- Run a function n times --
def _run(func, n=1) -> list:
    results = []
    for _ in range(n):
        results.append(func())
    return results

# -- Retry a function --
def _retry(_func=None, *, n=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for _ in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
            raise last_exception
        return wrapper

    if _func is None:
        return decorator
    if callable(_func):
        return decorator(_func)

    raise TypeError("retry must be used as a decorator, optionally with 'n' argument")