import pygame, json
from utils import Util

KEYBIND_FILE = "data/config/keybinds.json"
with open(KEYBIND_FILE, "r") as f:
    KEYBINDS: dict = json.load(f)

class Bindings:
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def check(event: pygame.event.Event, action: str) -> bool:
        return KEYBINDS.get(action, None) == event.key
    
    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def get(action: str) -> int:
        return KEYBINDS.get(action, None)