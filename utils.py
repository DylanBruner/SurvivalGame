import pygame

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