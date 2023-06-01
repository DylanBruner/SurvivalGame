import inspect, os, sys, threading, time, pygame

def loadPackage(filename: str, globs: dict) -> None:
    with open(filename, 'r') as f:
        exec(f.read(), globs)

try:
    from cheatil import Cheatil
except ModuleNotFoundError:
    loadPackage('cheats\\cheatil.py', globals())

if not inspect.currentframe().f_back: # if we're not being called from within the game
    sys.exit(os.system("python main.py --debug-scripts=cheats\\inject.py"))

frame = inspect.currentframe().f_back
frame.f_globals["DEV_MODE"] = True # force dev mode

def gameViewOnDraw():
    inGame = False
    while not inGame:
        if frame.f_globals['environment'].viewport.__class__.__name__ == "GameView":
            inGame = True
        else: time.sleep(1)
    print("Detected game view, sleeping 10 seconds...")
    time.sleep(10)

    cheats = {
        'speedHack':   {'enabled': False, 'value': 10, 'key': 'NUM7', 'code': pygame.K_KP7},
        'fastStamina': {'enabled': True,  'value': 10, 'key': 'NUM8', 'code': pygame.K_KP8},
        'fastBreak':   {'enabled': False, 'value': 10, 'key': 'NUM9', 'code': pygame.K_KP9},
    }

    # ==================== Viewport Hooking ====================
    def draw(self, environment: dict):
        tempSurface = pygame.Surface(environment['window'].get_size())
        old = environment['window']
        environment['window'] = tempSurface
        self.original_draw(environment)
        environment['window'] = old

        if environment['viewport'].paused:
            environment['window'].blit(tempSurface, (0, 0))
            return
        
        tempSurface.blit(pygame.font.SysFont('Arial', 20).render("Cheats:", True, (255, 255, 255)), (10, 10))
        for i, cheat in enumerate(cheats):
            color = (255, 0, 0) if not cheats[cheat]['enabled'] else (0, 255, 0)
            tempSurface.blit(pygame.font.SysFont('Arial', 20).render(f"{cheats[cheat]['key']}) {cheat}: {cheats[cheat]['value']}", True, color), (20, 10 + (i + 1) * 20))


        environment['window'].blit(tempSurface, (0, 0))

    def onEvent(self, event: pygame.event.Event):
        self.original_onEvent(event)

        if event.type == pygame.KEYDOWN:
            for cheat in cheats:
                if event.key == cheats[cheat]['code']:
                    cheats[cheat]['enabled'] = not cheats[cheat]['enabled']

    patched = Cheatil.patchClass(frame.f_globals['environment'].viewport.__class__, {"draw": draw, "onEvent": onEvent})
    frame.f_globals['environment'].viewport = patched((800, 600), frame.f_globals['environment'], frame.f_globals['environment'].viewport.save)
    print("Patched game view")

threading.Thread(target=gameViewOnDraw).start()