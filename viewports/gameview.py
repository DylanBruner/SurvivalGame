import pygame, time

from components import *
from componentsystem import Viewport
from myenviorment import Environment
from utils import Util
from game.savemanager import SaveGame
from viewports.pausemenu import PauseMenu

class GameView(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment,
                 save: SaveGame = None):
        super().__init__(size, enviorment)
        self.save: SaveGame = save
        if self.save == None: raise Exception("No save file specified")

        self.paused: bool = False
        self.paused_overlay: Viewport = None

        self.setup()
    
    def setup(self):
        self.FPS_DISPLAY = TextDisplay(location=(10, 10), text="FPS: ???")
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.FPS_DISPLAY)
    
    def draw(self, enviorment: dict):
        if self.paused:
            if self.paused_overlay.closed:
                self.paused = False
                self.paused_overlay = None
                return
            self.paused_overlay.draw(enviorment)
            return
        
        super().draw(enviorment)
        if time.time() - self.FPS_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.FPS_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.FPS_DISPLAY.setText(f"FPS: {enviorment['clock'].get_fps():.0f}")

    def onEvent(self, event: pygame.event.Event):
        if self.paused:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = True
                self.paused_overlay = PauseMenu(self.size, self.enviorment)
                self.enviorment['overlays'].append(self.paused_overlay)
                return