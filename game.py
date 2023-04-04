import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame
from viewports.mainmenu import MainMenu
from utils import Util
from myenviorment import Environment

#https://opengameart.org/content/iron-plague-pointercursor

pygame.init()

# keeping most of the important stuff in a dict lets me pass it around easily, probably not the best way to do it but it works
environment = Environment(**{
    "GAME_NAME": "A Game",
    "window": pygame.display.set_mode((800, 600), pygame.RESIZABLE),
    "last_viewport": None,
    "current_size": (800, 600),
    "overlays": [],
    "clock": pygame.time.Clock(),
    "time_delta": 0
})
environment.viewport = MainMenu(environment.current_size, environment)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.VIDEORESIZE:
            environment.viewport.resize(environment.current_size, (event.w, event.h))
            environment.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            environment.current_size = (event.w, event.h)
        
        environment.viewport.onEvent(event)

    environment.window.fill((255, 255, 255))
    
    environment.viewport.draw(environment)
    for overlay in environment.overlays:
        overlay.draw(environment) # basically just more viewports

    pygame.display.update()
    environment.time_delta = min(environment.clock.tick(1000), 500) # if we exceed 500ms, something is probably wrong so this'll help avoid
                                                                        # really bad lag spikes and weird behavior