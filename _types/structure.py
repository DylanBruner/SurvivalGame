import json, random

class LootTable:
    def __init__(self, items: dict):
        self.items: dict = items#{item_id: '', max: 0, min: 0}

    def roll(self) -> list[list[int, int]]:
        items = []

        for item in self.items:
            items.append([item['id'], random.randint(item['min'], item['max'])])

        return items
    
    def __repr__(self) -> str:
        return f"LootTable(items={self.items})"

class LootSpawn:
    def __init__(self, location: tuple[int, int], table: LootTable):
        self.location = location
        self.table    = table

    def __repr__(self) -> str:
        return f"LootSpawn(location={self.location}, table={self.table})"

class Structure:
    def __init__(self, id: str, spawn_chance: int, 
                 structure: list[list[int]], generation: dict):
        self._generation: dict = generation # this shouldn't really be used save for the initial load of the structure
        
        self.id: str = id
        self.spawn_chance: int = spawn_chance
        self.structure: list[list[int]] = structure

        self.lootSpawns: list[LootSpawn] = []
        if 'loot' in generation:
            for spawn in generation['loot']:
                self.lootSpawns.append(LootSpawn((spawn['x'], spawn['y']), LootTable(spawn['items'])))

    @staticmethod
    def fromID(id: str) -> 'Structure':
        with open("data/config/structures.json", 'r') as f:
            data = json.load(f)
        
        return Structure(id, data[id]['spawn_chance'], data[id]['structure'], data[id]['generation'])