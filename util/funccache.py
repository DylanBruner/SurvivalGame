_CACHE = {}

class Cache:
    @staticmethod
    def cache(maxLength: int = 100):
        """
        Decorator that caches the return value of a function for a given set of arguments.
        """
        def wrapper(func):
            def inner(*args, **kwargs):
                key = str(args) + str(kwargs)
                if key in _CACHE:
                    return _CACHE[key]
                else:
                    value = func(*args, **kwargs)
                    _CACHE[key] = value
                    if len(_CACHE) > maxLength:
                        _CACHE.pop(list(_CACHE.keys())[0])
                    return value
            return inner
        return wrapper