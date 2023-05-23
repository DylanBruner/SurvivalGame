import pygame, util.myenvironment as myenvironment, util.utils as utils, time, sys, importlib
from util.timer import DebugTimer
import tasks.backgroundsave as backgroundsave
from tasks.taskmanager import TaskManager
from util.pylambda import _if
import game.save.world as world
import viewports.mainmenu as mainmenu

#https://opengameart.org/content/iron-plague-pointercursor

pygame.init()
DEV_MODE = True # if true, the game will let you do some things that you shouldn't be able to do in a normal game

STEPPING_MODE = False # if true, the game will only update when you press enter, only works for game logic and some rendering
STEPS         = 0 # how many steps we have that haven't been processed yet

# keeping most of the important stuff in a dict lets me pass it around easily, probably not the best way to do it but it works
environment = myenvironment.Environment(**{
    "GAME_NAME": "A Game",
    "window": pygame.display.set_mode((800, 600), pygame.RESIZABLE),
    "current_size": (800, 600),
    "overlays": [],
    "clock": pygame.time.Clock(),
    "time_delta": 0,
    "fullscreen": False,
    "debugTimer": DebugTimer(),
    "taskManager": TaskManager().start()
})
environment.viewport = mainmenu.MainMenu(environment.current_size, environment)

world.postLoad() # some more asset processing that needs to be done after pygame is fully initialized

# Register background tasks ================================================
environment.taskManager.register(backgroundsave.task, environment).setInterval(60) # Autosave every 60 seconds

if "--dev" in sys.argv:
    DEV_MODE = True

for arg in sys.argv:
    if arg.startswith("--debug-scripts="):
        for script in arg.split("=")[1].split(","):
            with open(script, 'r') as f:
                exec(f.read(), globals())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if hasattr(environment.viewport, "save"):
                environment.viewport.save.save()
            environment.taskManager.stop()
            pygame.quit()
            quit()

        if event.type == pygame.VIDEORESIZE:
            environment.viewport.resize(environment.current_size, (event.w, event.h))
            environment.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            environment.current_size = (event.w, event.h)
        
        if event.type == pygame.KEYDOWN:
            # DEV/STEPPING MODE
            if event.key == pygame.K_F3 and DEV_MODE:
                STEPPING_MODE = (not STEPPING_MODE)
                print("[DEV] Stepping mode:", STEPPING_MODE)
            if STEPPING_MODE and event.key == pygame.K_RETURN and DEV_MODE:
                STEPS += 1
            
            # DEV/RELOADING Warning: this is a very bad thing to use!
            if event.key == pygame.K_F5 and DEV_MODE:
                # draw the text 'reloading' in the middle of the screen in red
                font = pygame.font.SysFont("Arial", 32)
                text = font.render("Reloading!", True, (255, 0, 0))
                environment.window.blit(text, (environment.current_size[0] // 2 - text.get_width() // 2, (environment.current_size[1] // 2 - text.get_height() // 2) - 100))
                pygame.display.update()
                startTime = time.time()
                utils.Util.MonkeyUtils.reload(environment, globals())
                print(f"[DEV] Reloaded in {time.time() - startTime:.4f} seconds!")
            
            if event.key == pygame.K_F11:
                environment.window = pygame.display.set_mode(environment.window.get_size(), pygame.FULLSCREEN)
                environment.current_size = environment.window.get_size()
            
            if event.key == pygame.K_F9:
                print(environment.debugTimer._timeData)

        start = time.time()
        environment.viewport.onEvent(event)
        environment.debugTimer.manualTime("Viewport.onEvent", time.time() - start)

        # not exactly sure why this is here
        for overlay in environment.overlays:
            if not overlay.closed:
                start = time.time()
                overlay.onEvent(event)
                _if(DEV_MODE,
                    lambda: environment.debugTimer.manualTime(f"{overlay.__class__.__name__}.onEvent", time.time() - start))()
                    

    if STEPPING_MODE and STEPS == 0:
        continue
    elif STEPPING_MODE: STEPS -= 1
    
    environment.window.fill((255, 255, 255))
    
    start = time.time()
    environment.viewport.draw(environment)
    environment.debugTimer.manualTime("Viewport.draw", time.time() - start)

    for overlay in environment.overlays:
        if not overlay.closed:
            start = time.time()
            overlay.draw(environment)
            _if(DEV_MODE, 
                lambda: environment.debugTimer.manualTime(f"{overlay.__class__.__name__}.draw", time.time() - start))()
                
    pygame.display.update()
    environment.time_delta = min(environment.clock.tick(60), 500) if not STEPPING_MODE else 10