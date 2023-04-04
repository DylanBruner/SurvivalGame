import json
from game.world import World

class SaveGame:
    def __init__(self, save_file: str = None):
        self.save_file: str  = save_file
        self.save_data: dict = None

        if save_file != None:
            self.loadSave(save_file)
        
    def loadSave(self, save_file: str):
        with open(f"data/saves/{save_file}", 'r') as f:
            self.save_data = json.load(f)

    @staticmethod
    def createNewSave(save_file: str) -> 'SaveGame':
        save_data = {
            "save_name": save_file.replace("_"," ").replace(".json","").title(),
            "player": {
                "inventory": {},
                "money": 0,
                "health": 100,
                "max_health": 100,
                "level": 1,
                "xp": 0,
            },
            "world": World().save()
        }

        with open(f"data/saves/{save_file}", 'w') as f:
            json.dump(save_data, f)
        
        return SaveGame(save_file)