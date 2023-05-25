import pygame, util.myenvironment as myenvironment, util.utils as utils, time, sys
from util.timer import DebugTimer
import tasks.backgroundsave as backgroundsave
from tasks.taskmanager import TaskManager
from util.pylambda import _if
import game.save.world as world
import viewports.mainmenu as mainmenu

#opengameart.org - lots of art taken from here

pygame.init()
DEV_MODE = True
"""
If DEV_MODE is true you will be able to do the following,
 - [F3] Enable stepping mode, (hit enter to step through frames)
 - [F5] Reload the game (re-import everything) makes development faster and has only broken like twice
 - [F9] Print out timing data that shows how long some elements of the game take to execute
"""

STEPPING_MODE = False # if true, the game will only update when you press enter, only works for game logic and some rendering
STEPS         = 0 # how many steps we have that haven't been processed yet

"""
I keep most all of the important variables inside what's basically a glorified dictionary
so it can be easily passed around the code.

The double stars '**' means expand to kwargs or pass each thing as a keyword argument.
Really theres no reason I couldn't just pass each thing as a keyword argument initally.
So I'm not 100% sure why I went with this? Maybe I thought it looked nicer lol.. idk.
"""
environment = myenvironment.Environment(**{
    "GAME_NAME": "A Game", # Because I couldn't/still cant pick a game name
    "window": pygame.display.set_mode((800, 600), pygame.RESIZABLE),
    "current_size": (800, 600),
    "overlays": [],
    "clock": pygame.time.Clock(), # clock for tracking and keeping a given FPS
    "time_delta": 0, # Time change between frames
    "fullscreen": False,
    "debugTimer": DebugTimer(),
    "taskManager": TaskManager().start() # Allows tasks to be registered that run in the background
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
            """
            If we're in a game save it, really this should be handled via a event 
            inside the GameView class
            """
            if hasattr(environment.viewport, "save"):
                environment.viewport.save.save()
            environment.taskManager.stop()
            pygame.quit()
            sys.exit() # need to use this instead of quit cause quit doesn't work in binary form

        if event.type == pygame.VIDEORESIZE:
            environment.viewport.resize(environment.current_size, (event.w, event.h))
            environment.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            environment.current_size = (event.w, event.h)
        
        if event.type == pygame.KEYDOWN:
            # DEV/STEPPING MODE
            if event.key == pygame.K_F3 and DEV_MODE:
                STEPPING_MODE = (not STEPPING_MODE)
                print("[DEV] Stepping mode:", STEPPING_MODE)
            # Add a step to the queue
            if STEPPING_MODE and event.key == pygame.K_RETURN and DEV_MODE:
                STEPS += 1
            
            # DEV/RELOADING Warning: this is a very bad thing to use! (it actually works reall well)
            if event.key == pygame.K_F5 and DEV_MODE:
                # draw the text 'reloading' in the middle of the screen in red
                font = pygame.font.SysFont("Arial", 32)
                text = font.render("Reloading!", True, (255, 0, 0))
                environment.window.blit(text, (environment.current_size[0] // 2 - text.get_width() // 2, (environment.current_size[1] // 2 - text.get_height() // 2) - 100))
                pygame.display.update()
                startTime = time.time()
                utils.Util.MonkeyUtils.reload(environment, globals())
                print(f"[DEV] Reloaded in {time.time() - startTime:.4f} seconds!")
            
            # Full screen mode, kind of works
            if event.key == pygame.K_F11:
                environment.window = pygame.display.set_mode(environment.window.get_size(), pygame.FULLSCREEN)
                environment.current_size = environment.window.get_size()
            
            # Print out timing information
            if event.key == pygame.K_F9 and DEV_MODE:
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
    """                
    Code for stepping, the queue would really never go above 1 step unless something is take a
    LONG time to run
    """
    if STEPPING_MODE and STEPS <= 0:
        continue
    elif STEPPING_MODE: STEPS -= 1
    
    environment.window.fill((255, 255, 255)) # Clear the window

    # Call and time the main viewports draw function 
    start = time.time()
    environment.viewport.draw(environment)
    environment.debugTimer.manualTime("Viewport.draw", time.time() - start)
    
    # Call and time any overlays draw functions
    for overlay in environment.overlays:
        if not overlay.closed:
            start = time.time()
            overlay.draw(environment)
            _if(DEV_MODE, 
                lambda: environment.debugTimer.manualTime(f"{overlay.__class__.__name__}.draw", time.time() - start))()
                
    pygame.display.update()
    """
    The goal of using time delta or delta time is just to make sure everything happens at the 
    same speed regardless of the FPS.
    """
    environment.time_delta = min(environment.clock.tick(60), 500) if not STEPPING_MODE else 10