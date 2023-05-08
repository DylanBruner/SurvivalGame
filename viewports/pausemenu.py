import pygame, time

from components.components import *
from components.componentsystem import Viewport
from util.myenvironment import Environment
from util.utils import Util
from game.misc.sounds import Sounds

class PauseMenu(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment):
        super().__init__(size, environment)
        self.setup()
    
    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        self.pause_text = TextDisplay(location=(10, 10), text="Paused")
        self.registerComponent(self.pause_text)
        self.resume_button = Button(location=(10, 30), size=(100, 30), text="Resume")
        self.resume_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), self.resume())
        self.registerComponent(self.resume_button)
        self.exit_button = Button(location=(10, 70), size=(100, 30), text="Exit")
        self.exit_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), self.exit())
        self.registerComponent(self.exit_button)

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)
    
    @Util.MonkeyUtils.autoErrorHandling
    def resume(self):
        self.closed = True
        self.environment['overlays'].remove(self)
    
    @Util.MonkeyUtils.autoErrorHandling
    def exit(self):
        self.environment.viewport.player.save(self.environment.viewport)
        self.environment.viewport.save.save() # save the game
        self.environment.viewport = Util.MonkeyUtils.getViewportFromName("mainmenu")(self.environment.viewport.size, self.environment)
        self.environment.last_viewports = [] # we don't want to go 'back' into the game
        self.closed = True
    
    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, environment: dict):
        super().draw(environment)

VIEWPORT_CLASS = PauseMenu