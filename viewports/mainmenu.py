import pygame
from componentsystem import Viewport
from components import *

class MainMenu(Viewport):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size)
        menutheme = self.theme.__class__()
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme

        self.setupMenu()

    def setupMenu(self):
        y_offset = self.size[1] / 4 - 100
        self.menu_text = TextDisplay((self.size[0] / 2 - 100 + DEFAULT_FONT.size("Main Menu")[0] / 4, 50 + y_offset), (200, 40), "Main Menu", pygame.font.SysFont("Arial", 40))
        self.play_button = Button((self.size[0] / 2 - 100, 150 + y_offset), (200, 40), "Play")
        self.options_button = Button((self.size[0] / 2 - 100, 200 + y_offset), (200, 40), "Options")
        self.quit_button = Button((self.size[0] / 2 - 100, 250 + y_offset), (200, 40), "Quit")

        self.registerComponents([self.menu_text, self.play_button, self.options_button, self.quit_button])
    
    def resize(self, old: tuple[int, int], new: tuple[int, int]):
        self.size = new
        # unregister all components
        self.components['components'] = []
        self.components['hooks'] = {}
        self.setupMenu()

    def draw(self, enviorment: dict):
        super().draw(enviorment)
        
        # custom draw code go here