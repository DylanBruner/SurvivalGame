import os, shutil, pygame

from components import *
from componentsystem import Viewport
from myenvironment import Environment
from utils import Util
from viewports.newsavemenu import NewSaveMenu
from viewports.gameview import GameView
from game.savemanager import SaveGame

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

        save_names = [name for name in list(os.listdir("data/saves")) if name.endswith(".json")][:3]
        nice_names = [name.replace("_", " ").replace(".json", "").title() for name in save_names][:3]

        self.save_buttons = []
        for i in range(len(save_names)):
            self.save_buttons.append(Button((self.size[0] / 2 - 100, 150 + i * 50), (200, 40), nice_names[i]))
            self.save_buttons[i].on_click = lambda save_file=save_names[i]: self.launchSave(save_file)
            self.registerComponent(self.save_buttons[i])
        
        if len(save_names) < 3:
            self.new_game_button = Button((self.size[0] / 2 - 100, 200 + len(save_names) * 50), (200, 40), "New Game")
            self.new_game_button.on_click = lambda: Util.launchViewport(self, NewSaveMenu(self.size, self.enviorment), self.enviorment)
            self.registerComponent(self.new_game_button, {'border_radius': 4})

        self.back_button = Button((self.size[0] / 2 - 100, 250 + len(save_names) * 50), (200, 40), "Back")
        self.back_button.on_click = lambda: Util.backViewport(self.enviorment)
        self.registerComponent(self.back_button, {'border_radius': 4})
    
    def launchSave(self, save_file: str):
        # check if the 'r' key is pressed
        if pygame.key.get_pressed()[pygame.K_r]:
            print("[INFO] Backing up save file...")
            shutil.copyfile(f"data/saves/{save_file}", f"data/saves/backup_{save_file}")
            print("[INFO] Backup complete!")
            print("[INFO] Attempting to repair/update save file...")
            SaveGame.repairSave(save_file)
            print("[INFO] Repair/update complete! attempting to load save file...")
        elif pygame.key.get_pressed()[pygame.K_l]:
            print("[INFO] Backing up save file...")
            shutil.copyfile(f"data/saves/{save_file}", f"data/saves/backup_{save_file}")
            print("[INFO] Backup complete!")
            print("[INFO] Regnerating map...")
            SaveGame.regenMap(save_file)
            print("[INFO] Regeneration complete! attempting to load save file...")

        save_game = SaveGame(save_file=save_file)
        game_view = GameView(self.size, self.enviorment, save_game)
        Util.launchViewport(self, game_view, self.enviorment)
    
    def draw(self, enviorment: dict):
        super().draw(enviorment)

VIEWPORT_CLASS = PlayGame