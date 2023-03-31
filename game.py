import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame
from componentsystem import Viewport, Component
from viewports.uidemo import UiDemo


pygame.init()

enviorment = {
    "window": pygame.display.set_mode((800, 600)),
    "viewport": UiDemo(),
    "clock": pygame.time.Clock(),
    "time_delta": 0
}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        enviorment["viewport"].onEvent(event)

    enviorment["window"].fill((255, 255, 255))
    
    enviorment["viewport"].draw(enviorment)

    pygame.display.update()
    enviorment["time_delta"] = enviorment["clock"].tick(1000)