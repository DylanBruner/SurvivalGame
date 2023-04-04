import json, random

class Tiles:
    EMPTY = 0 # Really shouldn't be used
    GRASS = 0

class World:
    def __init__(self, map_file: str = None, random_gen: bool = True, MAP_SIZE: tuple[int, int] = (800, 800)):
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
    
    def generateMap(self, seed: int = None):
        random.seed((random.randint(0, 100000) if seed == None else seed))
        self.map['seed'] = seed
        # fill map with grass
        self.map['map_data'] = [[Tiles.GRASS for _ in range(self.MAP_SIZE[0])] for _ in range(self.MAP_SIZE[1])]

        # Eventually i'll add some more random generation stuff here when i add more tile types