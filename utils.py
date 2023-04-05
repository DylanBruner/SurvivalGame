import pygame
from componentsystem import Viewport
from myenviorment import Environment

class Util:
    @staticmethod
    def loadSpritesheet(path: str, spriteSize: tuple, spriteCount: int, transparentColor: tuple = None):
        spritesheet = pygame.image.load(path).convert_alpha()
        if transparentColor:
            spritesheet.set_colorkey(transparentColor)
        sprites = []
        for i in range(spriteCount):
            sprites.append(spritesheet.subsurface((i * spriteSize[0], 0, spriteSize[0], spriteSize[1])))
        return sprites

    @staticmethod
    def launchViewport(old: Viewport, new: Viewport, enviorment: Environment) -> None:
        old.setCustomCursorEnabled(False)
        enviorment.viewport = new
        enviorment.last_viewports.append(old)
    
    @staticmethod
    def backViewport(enviorment: Environment) -> None:
        old = enviorment.viewport
        new = enviorment.last_viewports.pop()
        old.setCustomCursorEnabled(False)
        enviorment.viewport = new
    
    @staticmethod
    def distance(p1: tuple, p2: tuple) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    @staticmethod
    def getTileLocation(mouse_pos: tuple, player_pos: tuple, window_size: tuple, tile_size: int) -> tuple:
        startX = player_pos[0] - (window_size[0] // tile_size) // 2
        startY = player_pos[1] - (window_size[1] // tile_size) // 2
        return ((mouse_pos[0] // tile_size) + startX, (mouse_pos[1] // tile_size) + startY)