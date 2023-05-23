import inspect, os, sys, threading, time

def loadPackage(filename: str, globs: dict) -> None:
    with open(filename, 'r') as f:
        exec(f.read(), globs)

try:
    from cheatil import Cheatil
except ModuleNotFoundError:
    loadPackage('cheats\\cheatil.py', globals())

if not inspect.currentframe().f_back: # if we're not being called from within the game
    sys.exit(os.system("bin\\main-v1.0.1.exe --debug-scripts=cheats\\inject.py"))

frame = inspect.currentframe().f_back
frame.f_globals["DEV_MODE"] = True # force dev mode

# def setup(self, **kwargs):
#     self.original_setup()
#     self.menu_text.color = (255, 0, 0)

# patched = Cheatil.patchClass(frame.f_globals["environment"].viewport.__class__, 
#                                   {"setup": setup})
# frame.f_globals["environment"].viewport = patched((800, 600), frame.f_globals["environment"])

def myThread():
    inGame = False
    while not inGame:
        if frame.f_globals["environment"].viewport.__class__.__name__ == "GameView":
            inGame = True
        else:
            time.sleep(1)
    print("Detected game view, sleeping 10 seconds...")
    time.sleep(10)
    player = frame.f_globals["environment"].viewport.player
    def tick(self, keys_pressed, environment, *args, **kwargs):
        
        environment['time_delta'] = environment['time_delta'] * 10
        self.original_tick(keys_pressed, environment, *args, **kwargs)
        environment['time_delta'] = environment['time_delta'] / 10

    speedHackPlayer = Cheatil.patchClass(player.__class__, {"tick": tick})
    player = speedHackPlayer(frame.f_globals["environment"].viewport.save.save_data)
    frame.f_globals["environment"].viewport.player = player

threading.Thread(target=myThread).start()