_CACHE = {}

class Cache:
    @staticmethod
    def cache(maxLength: int = 100):
        """
        Decorator that caches the return value of a function for a given set of arguments.
        maxLength = the maximum number of cached values
        """
        def wrapper(func):
            def inner(*args, **kwargs):
                key = str(args) + str(kwargs)
                if key in _CACHE: # If cache value exists use it
                    return _CACHE[key]
                else:
                    value = func(*args, **kwargs)
                    _CACHE[key] = value # Add a cache value
                    if len(_CACHE) > maxLength: #If we're over the maxLength remove one from the start
                        _CACHE.pop(list(_CACHE.keys())[0])
                    return value
            return inner
        return wrapper