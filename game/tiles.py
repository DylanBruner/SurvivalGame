import json
from utils import Util

TILE_CFG_FILE = "data/config/tiles.json"
TILE_DATA: dict = None

with open(TILE_CFG_FILE, "r") as f:
    TILE_DATA: dict = json.load(f)

class Tile:
    def __init__(self, name: str, id: int, texture: str, durability: int, 
                 breaking_power: int, collidable: bool, breakable: bool,
                 background_id: int = None, drops: list[list[int, int]] = None):
        self.name = name
        self.id = id
        self.texture = texture
        self.durability = durability
        self.breaking_power = breaking_power
        self.collidable = collidable
        self.breakable = breakable
        self.background_id = background_id
        self.drops = drops
    
    def __repr__(self):
        return f"Tile(name={self.name}, id={self.id}, texture={self.texture}, durability={self.durability}, breaking_power={self.breaking_power}, collidable={self.collidable}, breakable={self.breakable}, background_id={self.background_id}, drops={self.drops})"

class Tiles:
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def getTile(id_name: int or str) -> Tile:
        if isinstance(id_name, int):
            for key, tile in TILE_DATA.items():
                if key == 'QUICK_MAPPINGS': continue
                if tile["id"] == id_name:
                    return Tile(**tile)
        elif isinstance(id_name, str):
            return Tile(**TILE_DATA[id_name])

    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def calculateHitPercent(breaking_power: int, req_power: int, durability: int) -> int:
        base = 100 / durability
        if breaking_power >= req_power:
            return base * breaking_power
    
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def getTexture(id_name: int or str) -> str:
        if isinstance(id_name, int):
            for tile in TILE_DATA.values():
                if tile["id"] == id_name:
                    return tile["texture"]
        elif isinstance(id_name, str):
            return TILE_DATA[id_name]["texture"]