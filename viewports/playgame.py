import os

import pygame

from components import *
from componentsystem import Viewport
from myenviorment import Environment
from utils import Util


class PlayGame(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment):
        super().__init__(size, enviorment)
        menutheme = self.theme.__class__()
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme
        self.setup()
    
    def setup(self):
        pygame.display.set_caption(f"{self.enviorment.GAME_NAME} - Play Game")
        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

        save_names = [name for name in list(os.listdir("data/saves")) if name.endswith(".json")]
        nice_names = [name.replace("_", " ").replace(".json", "").title() for name in save_names]

        self.save_buttons = []
        for i in range(len(save_names)):
            self.save_buttons.append(Button((self.size[0] / 2 - 100, 150 + i * 50), (200, 40), nice_names[i]))
            self.save_buttons[i].on_click = lambda save_file=save_names[i]: self.launchSave(save_file)
            self.registerComponent(self.save_buttons[i])
        
        self.back_button = Button((self.size[0] / 2 - 100, 200 + len(save_names) * 50), (200, 40), "Back")
        self.back_button.on_click = lambda: Util.launchViewport(self, self.enviorment.last_viewport, self.enviorment)
        self.registerComponent(self.back_button)
    
    def launchSave(self, save_file: str):
        print(f"Launching save: {save_file}")

    def draw(self, enviorment: dict):
        super().draw(enviorment)