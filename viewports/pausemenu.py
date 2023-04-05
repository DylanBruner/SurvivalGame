import pygame, time

from components import *
from componentsystem import Viewport
from myenvironment import Environment
from utils import Util

class PauseMenu(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment):
        super().__init__(size, enviorment)
        self.setup()
    
    def setup(self):
        self.pause_text = TextDisplay(location=(10, 10), text="Paused")
        self.registerComponent(self.pause_text)
        self.resume_button = Button(location=(10, 30), size=(100, 30), text="Resume")
        self.resume_button.on_click = self.resume
        self.registerComponent(self.resume_button)
        self.exit_button = Button(location=(10, 70), size=(100, 30), text="Exit")
        self.exit_button.on_click = self.exit
        self.registerComponent(self.exit_button)

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)
    
    def resume(self):
        self.closed = True
        self.enviorment['overlays'].remove(self)
    
    def exit(self):
        self.enviorment.viewport.save.save() # save the game
        self.enviorment.viewport = Util.MonkeyUtils.getViewportFromName("mainmenu")(self.enviorment.viewport.size, self.enviorment)
        self.enviorment.last_viewports = [] # we don't want to go 'back' into the game
        self.closed = True
    
    def draw(self, enviorment: dict):
        super().draw(enviorment)

VIEWPORT_CLASS = PauseMenu