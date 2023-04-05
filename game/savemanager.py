import json
from game.world import World

BLANK_SAVE = {
    "save_name": "",
    "player": {
        "inventory": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "money": 0,
        "health": 100,
        "max_health": 100,
        "max_stamina": 100,
        "level": 1,
        "xp": 0,
        "x": 0,
        "y": 0,
    },
    "day_count": 0,
    "game_time": 0,
    "world": []
}


class SaveGame:
    def __init__(self, save_file: str = None):
        self.save_file: str = save_file
        self.save_data: dict = None

        if save_file != None:
            self.loadSave(save_file)

    def save(self) -> None:
        with open(f"data/saves/{self.save_file}", 'w') as f:
            json.dump(self.save_data, f)

    def loadSave(self, save_file: str):
        with open(f"data/saves/{save_file}", 'r') as f:
            self.save_data = json.load(f)

    def getTile(self, x: int, y: int) -> int:
        return self.save_data['world']['map_data'][y][x]

    def setTile(self, x: int, y: int, tile: int):
        self.save_data['world']['map_data'][y][x] = tile
    
    @staticmethod
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
    def createNewSave(save_file: str) -> 'SaveGame':
        save_data = {
            "save_name": save_file.replace("_", " ").replace(".json", "").title(),
            "player": {
                "inventory": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                "money": 0,
                "health": 100,
                "max_health": 100,
                "max_stamina": 100,
                "level": 1,
                "xp": 0,
                "x": 0,
                "y": 0,
                "day_counter": 0
            },
            "game_time": 0,
            "world": World().save()
        }

        with open(f"data/saves/{save_file}", 'w') as f:
            json.dump(save_data, f)

        return SaveGame(save_file)
