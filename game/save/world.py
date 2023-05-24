import pygame, random
from util.utils import Util

TILE_SIZE = 32

class TileIDS: # Tile IDS for quick reference
    EMPTY = 0 # Really shouldn't be used
    GRASS = 1
    WATER = 2
    STONE = 3
    TREE_V1 = 4 # Variation 1-4
    TREE_V2 = 5
    TREE_V3 = 6
    TREE_V4 = 7
    WOOD    = 8
    CHEST   = 9
    SAND    = 10

TEXTURE_MAPPINGS = { # TileID -> Texture Mapping
    TileIDS.EMPTY: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    TileIDS.GRASS: pygame.transform.scale(pygame.image.load('data/assets/world/grass/1.jpg'), (TILE_SIZE, TILE_SIZE)),
    TileIDS.STONE: pygame.transform.scale(pygame.image.load('data/assets/world/stones/Tileable1k.png'), (TILE_SIZE, TILE_SIZE)),
    TileIDS.WATER: pygame.transform.scale(pygame.image.load('data/assets/world/water.jpg'), (TILE_SIZE, TILE_SIZE)),

    TileIDS.TREE_V1: None,
    TileIDS.TREE_V2: None,
    TileIDS.TREE_V3: None,
    TileIDS.TREE_V4: None,

    TileIDS.WOOD: pygame.transform.scale(pygame.image.load('data/assets/world/light_wood.png'), (TILE_SIZE, TILE_SIZE)),
    TileIDS.CHEST: pygame.transform.scale(pygame.image.load('data/assets/world/chest.png'), (TILE_SIZE, TILE_SIZE)),
    TileIDS.SAND: pygame.transform.scale(pygame.image.load('data/assets/world/sand.jpg'), (TILE_SIZE, TILE_SIZE)),
}

def postLoad():
    _TREE_SPRITES = Util.loadSpritesheetAdvanced('data/assets/world/tree-variations.png', (64, 64), 8, 8)[4:]
    TEXTURE_MAPPINGS[TileIDS.TREE_V1] = pygame.transform.scale(_TREE_SPRITES[0], (TILE_SIZE, TILE_SIZE))
    TEXTURE_MAPPINGS[TileIDS.TREE_V2] = pygame.transform.scale(_TREE_SPRITES[1], (TILE_SIZE, TILE_SIZE))
    TEXTURE_MAPPINGS[TileIDS.TREE_V3] = pygame.transform.scale(_TREE_SPRITES[2], (TILE_SIZE, TILE_SIZE))
    TEXTURE_MAPPINGS[TileIDS.TREE_V4] = pygame.transform.scale(_TREE_SPRITES[3], (TILE_SIZE, TILE_SIZE))

    # (1, 0) -> (30, 31)
    CHEST = pygame.Surface((32, 32))
    CHEST.blit(TEXTURE_MAPPINGS[TileIDS.CHEST], (-1, 0), (1, 0, 32, 31))
    # scale up the x axis by a few pixels
    TEXTURE_MAPPINGS[TileIDS.CHEST] = pygame.transform.scale(CHEST, (36, 32))
    TEXTURE_MAPPINGS[TileIDS.CHEST] = pygame.transform.scale(TEXTURE_MAPPINGS[TileIDS.CHEST], (TILE_SIZE, TILE_SIZE))


class World:
    def __init__(self, map_file: str = None, random_gen: bool = True, MAP_SIZE: tuple[int, int] = (1600, 1600)):
        self.MAP_SIZE = MAP_SIZE
        self.map = {
            'seed': None,
            'map_data': None
        }
        if map_file != None:
            self.loadMap(map_file)
        elif random_gen:
            self.generateMap()
        else:
            raise Exception('No map file or random generation specified')
    
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def fromFile(path: str) -> 'World':
        return World(map_file = path)
    
    @Util.MonkeyUtils.autoErrorHandling
    def save(self) -> dict:
        return self.map

    @Util.MonkeyUtils.autoErrorHandling
    def generateMap(self, seed: int = None):
        # this code is pointless because we never actually use the seed
        random.seed((random.randint(0, 100000) if seed == None else seed))
        self.map['seed'] = seed