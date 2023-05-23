class _if:
    def __init__(self, condition: bool, true_value: callable):
        self._condition   = condition
        self._true_value  = true_value
        self._false_value = None

    def _else(self, false_value: callable) -> '_if':
        self._false_value = false_value
        return self
    
    def __call__(self, *args, **kwargs):
        if self._condition:
            return self._true_value(*args, **kwargs)
        else:
            return self._false_value(*args, **kwargs)