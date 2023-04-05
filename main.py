import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame, myenvironment, utils, time
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
})
environment.viewport = mainmenu.MainMenu(environment.current_size, environment)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if hasattr(environment.viewport, "save"):
                environment.viewport.save.save()
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
                startTime = time.time()
                utils.Util.MonkeyUtils.reload(environment, globals())
                print(f"[DEV] Reloaded in {time.time() - startTime:.4f} seconds!")
            
            if event.key == pygame.K_F11:
                environment.window = pygame.display.set_mode(environment.window.get_size(), pygame.FULLSCREEN)
                environment.current_size = environment.window.get_size()

        environment.viewport.onEvent(event)
        for overlay in environment.overlays:
            if not overlay.closed:
                overlay.onEvent(event)

    if STEPPING_MODE and STEPS == 0:
        continue
    elif STEPPING_MODE: STEPS -= 1
    
    environment.window.fill((255, 255, 255))
    
    environment.viewport.draw(environment)
    for overlay in environment.overlays:
        if not overlay.closed:
            overlay.draw(environment)

    pygame.display.update()
    environment.time_delta = min(environment.clock.tick(60), 500) # if we exceed 500ms, something is probably wrong so this'll help avoid
                                                                        # really bad lag spikes and weird behavior