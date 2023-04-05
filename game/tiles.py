import json

TILE_CFG_FILE = "data/config/tiles.json"

with open(TILE_CFG_FILE, "r") as f:
    TILE_DATA: dict = json.load(f)

class Tile:
    def __init__(self, name: str, id: int, texture: str, durability: int, breaking_power: int, collidable: bool, breakable: bool):
        self.name = name
        self.id = id
        self.texture = texture
        self.durability = durability
        self.breaking_power = breaking_power
        self.collidable = collidable
        self.breakable = breakable
    
    def __repr__(self):
        return f"Tile(name={self.name}, id={self.id}, texture={self.texture}, durability={self.durability}, breaking_power={self.breaking_power}, collidable={self.collidable}, breakable={self.breakable})"

class Tiles:
    @staticmethod
    def getTile(id_name: int or str) -> Tile:
        if isinstance(id_name, int):
            for tile in TILE_DATA.values():
                if tile["id"] == id_name:
                    return Tile(**tile)
        elif isinstance(id_name, str):
            return Tile(**TILE_DATA[id_name])

    @staticmethod
    def calculateHitPercent(breaking_power: int, req_power: int, durability: int) -> int:
        base = 100 / durability
        if breaking_power >= req_power:
            return base * breaking_power
    
    @staticmethod
    def getTexture(id_name: int or str) -> str:
        if isinstance(id_name, int):
            for tile in TILE_DATA.values():
                if tile["id"] == id_name:
                    return tile["texture"]
        elif isinstance(id_name, str):
            return TILE_DATA[id_name]["texture"]