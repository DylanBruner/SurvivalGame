import pygame

class Item:
    def __init__(self, item_id: int, count: int, texture: pygame.Surface, size: tuple = (34, 34)):
        self.item_id = item_id
        self.count   = count 
        self.texture = pygame.transform.scale(texture, size) # just in case

        # scale the texture down a little
        self.texture = pygame.transform.scale(self.texture, (size[0] - 5, size[1] - 5))

    def toTuple(self) -> tuple:
        return (self.item_id, self.count)
    
    def __repr__(self) -> str:
        return f"Item(id={self.item_id}, count={self.count})"