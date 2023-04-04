import pygame
from componentsystem import Viewport

class Environment:
    def __init__(self, **kwargs):
        # This is literally just so I can get code completion :)
        self.window: pygame.Surface
        self.viewport: Viewport
        self.overlays: list[Viewport]
        self.clock: pygame.time.Clock
        self.time_delta: int
        self.current_size: tuple[int, int]
        self.last_viewport: Viewport
        self.GAME_NAME: str
        self.__dict__.update(kwargs)
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value