import pygame, numpy, tqdm
import numba, os
from numba import jit
from PIL import Image

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

    @jit(nopython=True)
    def generateDiffuseMap(size: tuple, items: list[int]) -> list[list]:
        r_map = numpy.zeros((size[0], size[1]), dtype=numpy.int8)
        for x in range(size[0]):
            for y in range(size[1]):
                r_map[x][y] = items[numpy.random.randint(0, len(items))]
                
        return r_map

    # jit with object mode by default
    @jit(nopython=False, cache=True, parallel=True)
    def generateMeshedImage(size: tuple, diffuseMap: list[list], textures: list[Image.Image]) -> Image.Image:
        # check if cached
        if os.path.exists(f"data/cache/{size[0]}x{size[1]}_titlemesg.png"):
            return Image.open(f"data/cache/{size[0]}x{size[1]}_titlemesg.png")
        meshedImage = Image.new("RGBA", size)
        progbar = tqdm.tqdm(total=size[0] * size[1], desc="Generating meshed image")
        for x in range(size[0]):
            for y in range(size[1]):
                meshedImage.paste(textures[diffuseMap[x][y]], (x, y))
                progbar.update(1)
        
        f = open(f"data/cache/{size[0]}x{size[1]}_titlemesg.png", "wb")
        meshedImage.save(f, "PNG")
        f.close()
        
        return meshedImage