import time, threading, ctypes

class StoppableThread(threading.Thread):
    def __init__(self, func: callable):
        threading.Thread.__init__(self)
        self.func = func
    
    def run(self):
        self.func()
    
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    
    def stop(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

class Task:
    def __init__(self, func, *args, **kwargs):
        self._func     = func
        self._args     = args
        self._kwargs   = kwargs
        self._interval = 0
        self._oneTimeUse = False

        # === threading ===
        self._lastCalled = time.time()
    
    def setInterval(self, interval: float):
        self._interval = interval
    
    def setTimeout(self, delay: float):
        self._interval   = delay
        self._oneTimeUse = True

class TaskManager:
    def __init__(self):
        self._registered = []
    
    def register(self, func: callable, *args, **kwargs) -> Task:
        task = Task(func, *args, **kwargs)
        self._registered.append(task)
        return task

    def unregister(self, task: Task) -> bool:
        if task in self._registered:
            self._registered.remove(task)
            return True
    
    def _mainloop(self):
        while True:
            task: Task
            for task in self._registered:
                if time.time() - task._lastCalled >= task._interval:
                    task._func(*task._args, **task._kwargs)
                    task._lastCalled = time.time()

                    if task._oneTimeUse:
                        self.unregister(task)
            time.sleep(0.001)
    
    def start(self) -> 'TaskManager':
        self._thread = StoppableThread(self._mainloop)
        self._thread.start()
        return self
    
    def stop(self):
        self._thread.stop()