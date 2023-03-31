import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame
from viewports.uidemo import UiDemo
from utils import Util

pygame.init()

# keeping most of the important stuff in a dict lets me pass it around easily, probably not the best way to do it but it works
enviorment = {
    "window": pygame.display.set_mode((800, 600)),
    "viewport": UiDemo(),
    "overlays": [],
    "clock": pygame.time.Clock(),
    "time_delta": 0
}
# 18x18
enviorment["viewport"].setCursor(Util.loadSpritesheet("assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
enviorment["viewport"].setCustomCursorEnabled(True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        enviorment["viewport"].onEvent(event)

    enviorment["window"].fill((255, 255, 255))
    
    enviorment["viewport"].draw(enviorment)
    for overlay in enviorment["overlays"]:
        overlay.draw(enviorment) # basically just more viewports

    pygame.display.update()
    enviorment["time_delta"] = min(enviorment["clock"].tick(1000), 500) # if we exceed 500ms, something is probably wrong so this'll help avoid
                                                                        # really bad lag spikes and weird behavior