import pygame, random
from utils import Util

TILE_SIZE = 32

class TileIDS:
    EMPTY = 0 # Really shouldn't be used
    GRASS = 1
    WATER = 2
    STONE = 3
    TREE_V1 = 4 # Variation 1-4
    TREE_V2 = 5
    TREE_V3 = 6
    TREE_V4 = 7
    WOOD = 8


TEXTURE_MAPPINGS = {
    TileIDS.EMPTY: pygame.Surface((32, 32)),
    TileIDS.GRASS: pygame.transform.scale(pygame.image.load('data/assets/world/grass/1.jpg'), (32, 32)),
    TileIDS.STONE: pygame.transform.scale(pygame.image.load('data/assets/world/stones/Tileable1k.png'), (32, 32)),
    TileIDS.WATER: pygame.transform.scale(pygame.image.load('data/assets/world/water.jpg'), (32, 32)),

    TileIDS.TREE_V1: None,
    TileIDS.TREE_V2: None,
    TileIDS.TREE_V3: None,
    TileIDS.TREE_V4: None,

    TileIDS.WOOD: pygame.transform.scale(pygame.image.load('data/assets/world/light_wood.png'), (32, 32))
}

def postLoad():
    _TREE_SPRITES = Util.loadSpritesheetAdvanced('data/assets/world/tree-variations.png', (64, 64), 8, 8)[4:]
    TEXTURE_MAPPINGS[TileIDS.TREE_V1] = pygame.transform.scale(_TREE_SPRITES[0], (32, 32))
    TEXTURE_MAPPINGS[TileIDS.TREE_V2] = pygame.transform.scale(_TREE_SPRITES[1], (32, 32))
    TEXTURE_MAPPINGS[TileIDS.TREE_V3] = pygame.transform.scale(_TREE_SPRITES[2], (32, 32))
    TEXTURE_MAPPINGS[TileIDS.TREE_V4] = pygame.transform.scale(_TREE_SPRITES[3], (32, 32))

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
    def fromFile(path: str) -> 'World':
        return World(map_file = path)
    
    def save(self) -> dict:
        return self.map
    
    def getCirclePoints(self, center: int, radius: int, fill: bool) -> list[tuple[int, int]]:
        points = []
        # use a 2d circle algorithm to get the points that way it has circle-like edges
        # but include a little bit of randomness to make it look more natural
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                if x**2 + y**2 <= radius**2:
                    # check if the point is in the map
                    if center[0] + x >= 0 and center[0] + x < self.MAP_SIZE[0] and center[1] + y >= 0 and center[1] + y < self.MAP_SIZE[1]:
                        points.append((center[0] + x, center[1] + y))

                        # add a little bit of randomness to the points
                        if random.randint(0, 100) < 10:
                            if center[0] + x + 1 >= 0 and center[0] + x + 1 < self.MAP_SIZE[0] and center[1] + y >= 0 and center[1] + y < self.MAP_SIZE[1]:
                                points.append((center[0] + x + 1, center[1] + y))
        return points
    
    def generateMap(self, seed: int = None):
        random.seed((random.randint(0, 100000) if seed == None else seed))
        self.map['seed'] = seed
        # fill map with grass
        self.map['map_data'] = [[TileIDS.GRASS for _ in range(self.MAP_SIZE[0])] for _ in range(self.MAP_SIZE[1])]
        # add some stone
        for _ in range(1500):
            stone_start = (random.randint(0, self.MAP_SIZE[0] - 1), random.randint(0, self.MAP_SIZE[1] - 1))
            points = self.getCirclePoints(stone_start, random.randint(2, 5), True)
            for point in points:
                self.map['map_data'][point[1]][point[0]] = TileIDS.STONE

        # pick a random spot to start the water
        for _ in range(1200):
            water_start = (random.randint(0, self.MAP_SIZE[0] - 1), random.randint(0, self.MAP_SIZE[1] - 1))
            points = self.getCirclePoints(water_start, random.randint(5, 10), True)
            for point in points:
                self.map['map_data'][point[1]][point[0]] = TileIDS.WATER
        
        # pick random empty spots to place trees
        for _ in range(5500):
            location = (random.randint(0, self.MAP_SIZE[0] - 1), random.randint(0, self.MAP_SIZE[1] - 1))
            # while self.map['map_data'][location[1]][location[0]] != TileIDS.EMPTY:
                # location = (random.randint(0, self.MAP_SIZE[0] - 1), random.randint(0, self.MAP_SIZE[1] - 1))
            
            self.map['map_data'][location[1]][location[0]] = random.choice([TileIDS.TREE_V1, TileIDS.TREE_V2, TileIDS.TREE_V3, TileIDS.TREE_V4])