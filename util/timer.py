import time

class DebugTimer:
    def __init__(self):
        self._timeData = {}
    
    # Function wrapper that will time a function
    def trackFunc(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            self._timeData[func.__name__] = end - start
            return result
        return wrapper

    def manualTime(self, name: str, time: float or int) -> None:
        self._timeData[name] = time