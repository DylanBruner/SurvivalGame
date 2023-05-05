import inspect, os, importlib, colorama, time
#POC that doesn't quite work yet

_data = {
    "LiveLoad": {
        "enabled": True,
        "prefix": f"{colorama.Fore.RED}[LiveLoad/{colorama.Fore.LIGHTRED_EX}LiveLoad{colorama.Fore.RED}]{colorama.Fore.RESET} ",
        "registered_functions": {}
    }
}

class LiveLoad:
    @staticmethod
    def register(func: callable):
        filename = inspect.getfile(func)
        if inspect.isclass(func):
            func_name = func.__name__
        else:
            func_name = func.__qualname__

        def wrapper(*args, **kwargs):
            # re-import module
            module_name = os.path.splitext(os.path.basename(filename))[0]
            module = importlib.import_module(module_name)

            # get function
            func = getattr(module, func_name)
            print(func)
            return func(*args, **kwargs)
        return wrapper
    
class Test:
    @LiveLoad.register
    def testFunction(self):
        print("Hello World!")

while True:
    Test().testFunction()
    time.sleep(1)