import sys

import pygame

from components.components import *
from components.componentsystem import Viewport
from game.misc.lang import Lang
from game.misc.sounds import Sounds
from util.myenvironment import Environment
from util.utils import Util
from viewports.playgame import PlayGame
from viewports.settingsmenu import SettingsMenu


class MainMenu(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment):
        super().__init__(size, environment)
        menutheme = self.theme.__class__()
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme

        self.setup()

    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        self.lang = Lang()
        
        pygame.display.set_caption(f"{self.environment.GAME_NAME} - Main Menu")
        y_offset = self.size[1] / 4 - 100
        self.menu_text = TextDisplay(location=(self.size[0] / 2 - 100 + DEFAULT_FONT.size("Main Menu")[0] / 4, 50 + y_offset), text="Main Menu", font=pygame.font.SysFont("Arial", 40))
        self.play_button = Button((self.size[0] / 2 - 100, 150 + y_offset), (200, 40), self.lang.get(Lang.MENU_ACTION_PLAY))
        self.options_button = Button((self.size[0] / 2 - 100, 200 + y_offset), (200, 40), self.lang.get(Lang.MENU_ACTION_OPTIONS))
        self.quit_button = Button((self.size[0] / 2 - 100, 250 + y_offset), (200, 40), self.lang.get(Lang.MENU_ACTION_QUIT))
        
        # Button callbacks
        self.quit_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), pygame.quit(), self.environment.taskManager.stop(), sys.exit())
        self.options_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.launchViewport(self, SettingsMenu(self.size, self.environment), self.environment))
        self.play_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.launchViewport(self, PlayGame(self.size, self.environment), self.environment))

        self.registerComponents([self.menu_text, self.play_button, self.options_button, self.quit_button])
        
        # custom cursor
        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, environment: dict):
        super().draw(environment)

VIEWPORT_CLASS = MainMenu