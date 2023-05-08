import json, random
from game.save.world import World, TileIDS
from _types.structure import Structure, LootSpawn
from util.utils import Util

BLANK_SAVE = {
    "save_name": None,
    "player": {
        "inventory": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "storage": [[(0, 0) for _ in range(14)] for _ in range(4)], # 4 rows of 14
        "money": 0,
        "health": 100,
        "max_health": 100,
        "max_stamina": 100,
        "level": 1,
        "xp": 0,
        "x": 0,
        "y": 0,
        "xp_multiplier": 1,
        "coins": 0
    },
    "day_count": 0,
    "game_time": 0,
    "difficulty": {
        "blood_moon": True
    },
    "chests": {}, #ID: (x, y) = [(item, amount)]
    "world": []
}


class SaveGame:
    def __init__(self, save_file: str = None):
        self.save_file: str = save_file
        self.save_data: dict = None

        if save_file != None:
            self.loadSave(save_file)

    @Util.MonkeyUtils.autoErrorHandling
    def save(self) -> None:
        with open(f"data/saves/{self.save_file}", 'w') as f:
            json.dump(self.save_data, f)

    @Util.MonkeyUtils.autoErrorHandling
    def loadSave(self, save_file: str):
        with open(f"data/saves/{save_file}", 'r') as f:
            self.save_data = json.load(f)

    @Util.MonkeyUtils.autoErrorHandling
    def getTile(self, x: int, y: int) -> int:
        return self.save_data['world']['map_data'][y][x]

    @Util.MonkeyUtils.autoErrorHandling
    def setTile(self, x: int, y: int, tile: int):
        self.save_data['world']['map_data'][y][x] = tile
    
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def repairSave(save_file: str):
        with open(f"data/saves/{save_file}", 'r') as f:
            save_data = json.load(f)
        
        if save_data['world'] == []:
            save_data['world'] = World().save()
        
        # find any differences between the save and the blank save
        for key in BLANK_SAVE:
            if key not in save_data:
                print(f"[SAVE::REPAIR] Adding missing key: {key}")
                save_data[key] = BLANK_SAVE[key]
            elif type(save_data[key]) == dict:
                for key2 in BLANK_SAVE[key]:
                    if key2 not in save_data[key]:
                        print(f"[SAVE::REPAIR] Adding missing key: {key}/{key2}")
                        save_data[key][key2] = BLANK_SAVE[key][key2]
        
        with open(f"data/saves/{save_file}", 'w') as f:
            json.dump(save_data, f)
    
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def regenMap(save_file: str):
        with open(f"data/saves/{save_file}", 'r') as f:
            save_data = json.load(f)
        
        save_data['world'] = World().save()
        
        with open(f"data/saves/{save_file}", 'w') as f:
            json.dump(save_data, f)
        
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def createNewSave(save_file: str) -> 'SaveGame':
        save_data = BLANK_SAVE.copy()
        save_data['world'] = World().save()

        _map = save_data['world']['map_data']
        # World generation =====================================================
        # fill it with grass
        _map = [[TileIDS.GRASS for _ in range(1500)] for _ in range(1500)]
        POI_COUNT  = len(_map[0]) * len(_map) // 1000
        TREE_COUNT = len(_map[0]) * len(_map) // 100
        LAKE_COUNT = len(_map[0]) * len(_map) // 1000
        BOULDER_COUNT = len(_map[0]) * len(_map) // 1000

        PLACED_THINGS = []

        # first the structures
        with open('data/config/structures.json', 'r') as f:
            structures = list(json.load(f).keys())
        
        for l in range(POI_COUNT):
            structure = Structure.fromID(random.choice(structures))
            if random.random() > structure.spawn_chance:
                continue

            x = random.randint(0, len(_map[0]) - 1)
            y = random.randint(0, len(_map) - 1)

            # if the structure is too close to the edge, try again
            if x < 10 or x > len(_map[0]) - 10 or y < 10 or y > len(_map) - 10:
                continue
            # if the structure is too close to another structure, try again
            tooClose = False
            for x2, y2 in PLACED_THINGS:
                if Util.MathUtils.distance(x, y, x2, y2) < 20:
                    tooClose = True
                    break
            if tooClose:
                continue

            _map = Util.WorldUtils.placeStructure(_map, structure.structure, x, y)

            ls: LootSpawn = None
            for ls in structure.lootSpawns:
                chestContents = ls.table.roll()
                save_data['chests'][f"{x},{y}"] = chestContents

            PLACED_THINGS.append((x, y))

        print(f"[SAVE::NEW] Placed {len(PLACED_THINGS)} structures")

        # then the trees
        for l in range(TREE_COUNT):
            x, y = random.randint(0, len(_map[0]) - 1), random.randint(0, len(_map) - 1)
            if _map[y][x] != TileIDS.GRASS:
                continue
            _map[y][x] = random.choice([TileIDS.TREE_V1, TileIDS.TREE_V2, TileIDS.TREE_V3, TileIDS.TREE_V4])
        
        # then boulders
        for l in range(BOULDER_COUNT):
            x, y = random.randint(0, len(_map[0]) - 1), random.randint(0, len(_map) - 1)
            if _map[y][x] != TileIDS.GRASS:
                continue

            # if we're too close to the edge, try again
            if x < 10 or x > len(_map[0]) - 10 or y < 10 or y > len(_map) - 10:
                continue
            
            # make a randomish circle from 1 to 5 tiles wide around the point
            for y2 in range(y - random.randint(1, 5), y + random.randint(1, 5)):
                for x2 in range(x - random.randint(1, 5), x + random.randint(1, 5)):
                    if Util.MathUtils.distance(x, y, x2, y2) < 5:
                        _map[y2][x2] = TileIDS.STONE
            
        # then the lakes
        for l in range(LAKE_COUNT):
            x, y = random.randint(0, len(_map[0]) - 1), random.randint(0, len(_map) - 1)
            if _map[y][x] != TileIDS.GRASS:
                continue
            # if we're too close to the edge, try again
            if x < 10 or x > len(_map[0]) - 10 or y < 10 or y > len(_map) - 10:
                continue

            # if we're too close to another PLACED_THINGS, try again, within 100
            tooClose = False
            for x2, y2 in PLACED_THINGS:
                if Util.MathUtils.distance(x, y, x2, y2) < 25:
                    tooClose = True
                    break
            if tooClose:
                continue

            for y2 in range(y - 10, y + 10):
                for x2 in range(x - 10, x + 10):
                    if x2 < 0 or x2 >= len(_map[0]) or y2 < 0 or y2 >= len(_map):
                        continue
                    if Util.MathUtils.distance(x, y, x2, y2) > 10:
                        continue
                    _map[y2][x2] = TileIDS.WATER

            # add sand around the edges of the lake
            for y2 in range(y - 11, y + 11):
                for x2 in range(x - 11, x + 11):
                    if x2 < 0 or x2 >= len(_map[0]) or y2 < 0 or y2 >= len(_map):
                        continue
                    if Util.MathUtils.distance(x, y, x2, y2) > 10:
                        continue
                    if _map[y2][x2] == TileIDS.WATER:
                        for y3 in range(y2 - 1, y2 + 1):
                            for x3 in range(x2 - 1, x2 + 1):
                                if x3 < 0 or x3 >= len(_map[0]) or y3 < 0 or y3 >= len(_map):
                                    continue
                                if _map[y3][x3] == TileIDS.GRASS:
                                    _map[y3][x3] = TileIDS.SAND

            PLACED_THINGS.append((x, y))

        save_data['world']['map_data'] = _map
        # ======================================================================

        with open(f"data/saves/{save_file}", 'w') as f:
            json.dump(save_data, f)

        return SaveGame(save_file)