import os, json
from typing import Any

class Config:
    SAVE_TREE = {
        "save_name": "default",
        "save_data": {
            "inventory": [],
            "money": 0,
            "health": 100,
            "max_health": 100,
            "level": 1,
            "xp": 0,
        }
    }

class SaveFile:
    def __init__(self, target: str, save_name: str = ""):
        self.target = target

        if not os.path.exists(self.target): # create the save file if we need to
            with open(self.target, "w") as f:
                cfg = Config.SAVE_TREE.copy()
                cfg["save_name"] = save_name
                json.dump(cfg, f, indent=2)

    def __getitem__(self, key: str) -> Any:
        with open(self.target, "r") as f:
            return json.load(f)[key]
        
    def get(self) -> dict:
        with open(self.target, "r") as f:
            return json.load(f)
    
    def set(self, data: dict) -> None:
        with open(self.target, "w") as f:
            json.dump(data, f, indent=2)