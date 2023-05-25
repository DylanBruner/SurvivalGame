import os
import shutil

import pygame

from components.components import *
from components.componentsystem import Viewport
from game.display.charselector import CharacterSelector
from game.display.images import Images
from game.misc.lang import Lang
from game.misc.sounds import Sounds
from game.save.savemanager import SaveGame
from util.myenvironment import Environment
from util.utils import Util
from viewports.gameview import GameView
from viewports.newsavemenu import NewSaveMenu


class PlayGame(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment):
        super().__init__(size, environment)
        menutheme = self.theme.__class__() # Create a barebones theme for the buttons
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme
        self.setup()
    
    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        """
        Where all the components are generated and registered along with any other code
        that needs to be ran every time this viewport is loaded
        """
        self.lang = Lang()
        
        # Custom cursor and game title
        pygame.display.set_caption(f"{self.environment.GAME_NAME} - {self.lang.get(Lang.GAME_DISPLAY_PLAY_GAME)}")
        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)
        
        # Get the save names
        save_names = [name for name in list(os.listdir("data/saves")) if name.endswith(".save")][:3]
        nice_names = [name.replace("_", " ").replace(".save", "").title() for name in save_names][:3]

        # Generate buttons for the saves, reloaded everytime you re-enter the menu
        self.save_buttons = []
        for i in range(len(save_names)):
            # self.save_buttons.append(Button((self.size[0] / 4 - 100, 150 + i * 50), (200, 40), nice_names[i]))
            self.save_buttons.append(ImageButton((self.size[0] / 4 - 100, 50 + (i * 50)), Images().BUTTON_IDLE, Images().BUTTON_CLICK, Images().BUTTON_HOVER, text=nice_names[i], text_color=(0, 0, 0)))
            self.save_buttons[i].on_click = lambda save_file=save_names[i]: (Sounds.playSound(Sounds.MENU_CLICK), self.launchSave(save_file))
            self.registerComponent(self.save_buttons[i])
        
        # Only show the 'New Game' button if there is less than three created saves
        if len(save_names) < 3:
            self.new_game_button = ImageButton((self.size[0] / 4 - 100, 230 + (len(save_names) * 50)),
                                                  Images().BUTTON_IDLE, Images().BUTTON_CLICK, Images().BUTTON_HOVER, text=self.lang.get(Lang.MENU_ACTION_NEW_GAME), text_color=(0, 0, 0))
            self.new_game_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.launchViewport(self, NewSaveMenu(self.size, self.environment), self.environment))
            self.registerComponent(self.new_game_button)

        self.back_button = ImageButton((self.size[0] / 4 - 100, 300 + len(save_names) * 50), 
                                       Images().BUTTON_IDLE, Images().BUTTON_CLICK, Images().BUTTON_HOVER, text=self.lang.get(Lang.MENU_ACTION_BACK), text_color=(0, 0, 0))
        
        self.back_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.backViewport(self.environment))
        self.registerComponent(self.back_button) # Allows the button to actually draw and recive events

        self.character_selector = CharacterSelector((self.size[0] / 4 * 3 - 120, 40 + len(save_names) * 50))
        self.registerComponent(self.character_selector)
    
    @Util.MonkeyUtils.autoErrorHandling
    def launchSave(self, save_file: str):
        """
        Some more developer focused keybinds made to upgrade save files
        and regenerate the world
        """
        if pygame.key.get_pressed()[pygame.K_r]:
            print("[INFO] Backing up save file...")
            shutil.copyfile(f"data/saves/{save_file}", f"data/saves/{save_file}.bak")
            print("[INFO] Backup complete!")
            print("[INFO] Attempting to repair/update save file...")
            SaveGame.repairSave(save_file)
            print("[INFO] Repair/update complete! attempting to load save file...")
        elif pygame.key.get_pressed()[pygame.K_l]:
            print("[INFO] Backing up save file...")
            shutil.copyfile(f"data/saves/{save_file}", f"data/saves/{save_file}.bak")
            print("[INFO] Backup complete!")
            print("[INFO] Regnerating map...")
            SaveGame.regenMap(save_file)
            print("[INFO] Regeneration complete! attempting to load save file...")

        # Load the save, and launch the GameView viewport
        save_game = SaveGame(save_file=save_file)
        game_view = GameView(self.size, self.environment, save_game)
        Util.launchViewport(self, game_view, self.environment)
    
    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, environment: dict):
        super().draw(environment)

VIEWPORT_CLASS = PlayGame # Only used for reloading