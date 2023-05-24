import time

class DebugTimer:
    def __init__(self):
        self._timeData = {}
    
    def trackFunc(self, func):
        """
        Decorator that will time a function and store the time in the _timeData dictionary
        """
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            self._timeData[func.__name__] = end - start
            return result
        return wrapper

    def manualTime(self, name: str, time: float or int) -> None:
        """
        Manually add a log for a function
        """
        self._timeData[name] = time