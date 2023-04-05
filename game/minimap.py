from componentsystem import Component
from game.world import TILE_SIZE, TEXTURE_MAPPINGS
import pygame

class MiniMap(Component):
    def __init__(self, parent: Component = None):
        self.parent = parent
        super().__init__(location=(10, 10), size=(200, 200))

        self.SCALE_SIZE = (self.size[0] // TILE_SIZE, self.size[1] // TILE_SIZE)
        self.SCALED_TEXTURES = {}
    
    def draw(self, surface: pygame.Surface, enviorment: dict):
        pygame.draw.rect(surface, (255, 255, 255), (self.location[0], self.location[1], self.size[0], self.size[1]))
        mapSurface = pygame.Surface(self.parent.size)
        mapSurface.fill((255, 255, 255))

        #TODO: Figure out how to do this without lagging the game
        map: list[list[int]] = self.parent.save.save_data['world']['map_data']

        surface.blit(mapSurface, (self.location[0], self.location[1]))