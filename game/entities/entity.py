import pygame


class Entity:
    """
    Just a class for entities to inherit from
    """
    def __init__(self, location: tuple[int, int]):
        self.location = location
    
    def draw(self, screen: pygame.Surface) -> None:
        ...
    
    def onEvent(self, event: pygame.event.Event) -> None:
        ...