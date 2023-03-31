import pygame, time
from componentsystem import Viewport
from components import *
from utils import Util
from PIL import Image

class MainMenu(Viewport):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size)
        menutheme = self.theme.__class__()
        menutheme.THEME_TREE['Button']['border_radius'] = 0
        self.theme = menutheme

        self.setupMenu()
        self.generateBackground()

    def generateBackground(self):
        startTime = time.time()
        self.DIFFUSE_MAP = Util.generateDiffuseMap(self.size, [0, 1])
        print("Generated diffuse map in", time.time() - startTime, "seconds")
        # self.GRASS_TEXTURE_0 = pygame.image.load("data/assets/world/grass/1.jpg")
        # self.GRASS_TEXTURE_1 = pygame.image.load("data/assets/world/grass/2.jpg")
        self.GRASS_TEXTURE_0 = Image.open("data/assets/world/grass/1.jpg")
        self.GRASS_TEXTURE_1 = Image.open("data/assets/world/grass/2.jpg")

        startTime = time.time()
        meshed = Util.generateMeshedImage(self.size, self.DIFFUSE_MAP, [self.GRASS_TEXTURE_0, self.GRASS_TEXTURE_1])
        print("Generated meshed image in", time.time() - startTime, "seconds")
        self.MAP_SURFACE = pygame.Surface(self.size)
        self.MAP_SURFACE.blit(pygame.image.fromstring(meshed.tobytes(), meshed.size, meshed.mode), (0, 0))
        # do this more efficiently

    def setupMenu(self):
        y_offset = self.size[1] / 4 - 100
        self.menu_text = TextDisplay((self.size[0] / 2 - 100 + DEFAULT_FONT.size("Main Menu")[0] / 4, 50 + y_offset), (200, 40), "Main Menu", pygame.font.SysFont("Arial", 40))
        self.play_button = Button((self.size[0] / 2 - 100, 150 + y_offset), (200, 40), "Play")
        self.options_button = Button((self.size[0] / 2 - 100, 200 + y_offset), (200, 40), "Options")
        self.quit_button = Button((self.size[0] / 2 - 100, 250 + y_offset), (200, 40), "Quit")

        self.quit_button.on_click = lambda: quit()

        self.registerComponents([self.menu_text, self.play_button, self.options_button, self.quit_button])
    
    def resize(self, old: tuple[int, int], new: tuple[int, int]):
        self.size = new
        self.components['components'] = []
        self.components['hooks'] = {}
        self.setupMenu()
        self.generateBackground()

    def draw(self, enviorment: dict):
        # draw background
        enviorment["window"].blit(self.MAP_SURFACE, (0, 0))
        super().draw(enviorment)
        
        # custom draw code go here