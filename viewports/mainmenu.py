import pygame

from components import *
from componentsystem import Viewport
from myenviorment import Environment
from utils import Util
from viewports.playgame import PlayGame

class MainMenu(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment):
        super().__init__(size, enviorment)
        menutheme = self.theme.__class__()
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme

        self.setup()

    def setup(self):
        pygame.display.set_caption(f"{self.enviorment.GAME_NAME} - Main Menu")
        y_offset = self.size[1] / 4 - 100
        self.menu_text = TextDisplay(location=(self.size[0] / 2 - 100 + DEFAULT_FONT.size("Main Menu")[0] / 4, 50 + y_offset), text="Main Menu", font=pygame.font.SysFont("Arial", 40))
        self.play_button = Button((self.size[0] / 2 - 100, 150 + y_offset), (200, 40), "Play")
        self.options_button = Button((self.size[0] / 2 - 100, 200 + y_offset), (200, 40), "Options")
        self.quit_button = Button((self.size[0] / 2 - 100, 250 + y_offset), (200, 40), "Quit")

        self.quit_button.on_click = lambda: quit()
        self.play_button.on_click = lambda: Util.launchViewport(self, PlayGame(self.size, self.enviorment), self.enviorment)

        self.registerComponents([self.menu_text, self.play_button, self.options_button, self.quit_button])
        
        # custom cursor
        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

    def draw(self, enviorment: dict):
        super().draw(enviorment)