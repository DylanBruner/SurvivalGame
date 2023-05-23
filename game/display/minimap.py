import pygame
from components.componentsystem import Component
from game.save.world import TileIDS
from util.utils import Util

COLORS = {
    TileIDS.GRASS: (86, 125, 70),
    TileIDS.WATER: (3, 71, 112),
    TileIDS.STONE: (128, 127, 99),
}

class MiniMap(Component):
    def __init__(self, parent: Component = None):
        self.parent = parent
        self.SIZE   = 200
        super().__init__(location=(10, 10), size=(self.SIZE, self.SIZE))

    @Util.MonkeyUtils.autoErrorHandling
    def getMapBitmap(self) -> pygame.Surface:
        map: list[list[int]]         = self.parent.save.save_data['world']['map_data']
        player_loc: tuple[int, int]  = (int(self.parent.player.location[0]), int(self.parent.player.location[1]))

        bitmap: pygame.Surface = pygame.Surface((self.SIZE, self.SIZE))
        bitmap.fill((0, 0, 0))

        # draw the map self.SIZE around the player also use self.SCALE_TILE_SIZE to scale the map down
        cameraX = player_loc[0]
        cameraY = player_loc[1]

        # TODO: stop the black border from showing
        for x in range(cameraX - (self.SIZE // 2), player_loc[0] + (self.SIZE // 2)):
            for y in range(cameraY - (self.SIZE // 2), player_loc[1] + (self.SIZE // 2)):
                if x < 0 or y < 0 or x >= len(map) or y >= len(map[0]):
                    continue
                
                tile_id: int = map[x][y]
                tile_color: tuple[int, int, int] = COLORS.get(tile_id, (0, 0, 0))
                pygame.draw.rect(bitmap, tile_color, (x - (cameraX - (self.SIZE // 2)), y - (cameraY - (self.SIZE // 2)), 1, 1)) 

        return bitmap

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, environment: dict):
        player_facing: str = self.parent.player.facing # front, back, left, right

        mapSurface = pygame.Surface((self.SIZE, self.SIZE))
        pygame.draw.rect(mapSurface, (0, 0, 0), (0, 0, self.SIZE, self.SIZE), 1)

        # draw the map self.SIZE around the player
        bitmap: pygame.Surface = self.getMapBitmap()
        mapSurface.blit(bitmap, (0, 0))

        # draw a arrow in the direction the player is facing
        if player_facing == "back":
            pygame.draw.polygon(mapSurface, (255, 255, 255), ((self.SIZE // 2, self.SIZE // 2 - 5), (self.SIZE // 2 - 5, self.SIZE // 2 + 5), (self.SIZE // 2 + 5, self.SIZE // 2 + 5)))
        elif player_facing == "front":
            pygame.draw.polygon(mapSurface, (255, 255, 255), ((self.SIZE // 2, self.SIZE // 2 + 5), (self.SIZE // 2 - 5, self.SIZE // 2 - 5), (self.SIZE // 2 + 5, self.SIZE // 2 - 5)))
        elif player_facing == "left":
            pygame.draw.polygon(mapSurface, (255, 255, 255), ((self.SIZE // 2 - 5, self.SIZE // 2), (self.SIZE // 2 + 5, self.SIZE // 2 - 5), (self.SIZE // 2 + 5, self.SIZE // 2 + 5)))
        elif player_facing == "right":
            pygame.draw.polygon(mapSurface, (255, 255, 255), ((self.SIZE // 2 + 5, self.SIZE // 2), (self.SIZE // 2 - 5, self.SIZE // 2 - 5), (self.SIZE // 2 - 5, self.SIZE // 2 + 5)))

        surface.blit(mapSurface, self.location)