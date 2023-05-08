import pygame

from components.components import *
from components.componentsystem import Viewport
from util.myenvironment import Environment
from util.utils import Util
from game.save.savemanager import SaveGame
from game.misc.sounds import Sounds

class NewSaveMenu(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment):
        super().__init__(size, environment)
        self.setup()
    
    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        pygame.display.set_caption(f"{self.environment.GAME_NAME} - New Save")
        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

        self.save_name = TextInput(location=(self.size[0] / 2 - 100, 150), size=(200, 40), prompt_text="Save Name",
                                   max_length=20)
        self.save_name._selected = True
        self.registerComponent(self.save_name)

        self.create_button = Button((self.size[0] / 2 - 100, 200), (200, 40), "Create")
        self.create_button.on_click = lambda: self.createSave()
        self.registerComponent(self.create_button)

        self.back_button = Button((self.size[0] / 2 - 100, 300), (200, 40), "Back")
        self.back_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.backViewport(self.environment))
        self.registerComponent(self.back_button)
    
    @Util.MonkeyUtils.autoErrorHandling
    def createSave(self):
        Sounds.playSound(Sounds.MENU_CLICK)
        save_file = self.save_name.text.replace(" ", "_").lower().strip() + ".json"
        if save_file == ".json":
            return

        SaveGame.createNewSave(save_file)
        Util.backViewport(self.environment)
        self.environment['viewport'].reload()

VIEWPORT_CLASS = NewSaveMenu