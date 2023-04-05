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