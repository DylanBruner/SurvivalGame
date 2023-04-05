import pygame, time

from game.world import TILE_SIZE, TEXTURE_MAPPINGS, TileIDS
from game.invsystem import HotbarComponent
from components import *
from componentsystem import Viewport
from myenviorment import Environment
from utils import Util
from game.savemanager import SaveGame
from viewports.pausemenu import PauseMenu
from game.tiles import Tiles

class GameView(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment,
                 save: SaveGame = None):
        super().__init__(size, enviorment)
        self.save: SaveGame = save
        if self.save == None: raise Exception("No save file specified")
        self.theme = None # disable automatic themeing

        self.paused: bool = False
        self.paused_overlay: Viewport = None

        self.player_pos: tuple[int, int] = (0, 0)
        self.keys_pressed: dict[int, bool] = {}

        self.setup()
    
    def setup(self):
        self.FPS_DISPLAY = TextDisplay(location=(10, 10), text="FPS: ???", color=(255, 255, 255))
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.FPS_DISPLAY)

        # Game stuff
        self.hotbar = HotbarComponent(parent=self)
        self.registerComponent(self.hotbar)
    
    def canMove(self, dir: int) -> bool:
        # forward, backward, left, right
        projected_pos = None
        if dir == 0:
            projected_pos = (self.player_pos[0], self.player_pos[1] - 1)
        elif dir == 1:
            projected_pos = (self.player_pos[0], self.player_pos[1] + 1)
        elif dir == 2:
            projected_pos = (self.player_pos[0] - 1, self.player_pos[1])
        elif dir == 3:
            projected_pos = (self.player_pos[0] + 1, self.player_pos[1])
        else:
            raise Exception(f"Invalid direction: {dir}")

        # if projected_pos is out of bounds, return False
        if projected_pos[0] < 0 or projected_pos[0] >= len(self.save.save_data['world']['map_data'][0]):
            return False
        if projected_pos[1] < 0 or projected_pos[1] >= len(self.save.save_data['world']['map_data']):
            return False

        tileAt = self.save.save_data['world']['map_data'][projected_pos[1]][projected_pos[0]]        

        return not Tiles.getTile(tileAt).collidable
    
    def doGameLogic(self, enviorment: dict):
        # handle key presses
        if self.keys_pressed.get(pygame.K_a, False) and self.canMove(2):
            self.player_pos = (self.player_pos[0] - 1, self.player_pos[1])
        if self.keys_pressed.get(pygame.K_d, False) and self.canMove(3):
            self.player_pos = (self.player_pos[0] + 1, self.player_pos[1])
        if self.keys_pressed.get(pygame.K_w, False) and self.canMove(0):
            self.player_pos = (self.player_pos[0], self.player_pos[1] - 1)
        if self.keys_pressed.get(pygame.K_s, False) and self.canMove(1):
            self.player_pos = (self.player_pos[0], self.player_pos[1] + 1)
        
        # limit the player to the map
        self.player_pos = (max(0, min(self.player_pos[0], len(self.save.save_data['world']['map_data'][0]) - 1)),
                           max(0, min(self.player_pos[1], len(self.save.save_data['world']['map_data']) - 1)))
            
    def draw(self, enviorment: dict):
        if self.paused:
            if self.paused_overlay.closed:
                self.paused = False
                self.paused_overlay = None
                return
            self.paused_overlay.draw(enviorment)
            return
        
        self.doGameLogic(enviorment)

        if time.time() - self.FPS_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.FPS_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.FPS_DISPLAY.setText(f"FPS: {enviorment['clock'].get_fps():.0f}")

        self.enviorment['window'].fill((0, 0, 0))

        # draw the map
        map: list[list[int]] = self.save.save_data['world']['map_data']

        # it should be centered on the player
        VIEW_WIDTH  = self.size[0]
        VIEW_HEIGHT = self.size[1]

        startX = self.player_pos[0] - (VIEW_WIDTH // TILE_SIZE) // 2
        startY = self.player_pos[1] - (VIEW_HEIGHT // TILE_SIZE) // 2

        for y in range(startY, startY + (VIEW_HEIGHT // TILE_SIZE) + 1):
            for x in range(startX, startX + (VIEW_WIDTH // TILE_SIZE) + 1):
                if y < 0 or y >= len(map) or x < 0 or x >= len(map[y]):
                    continue

                tile: int = map[y][x]

                tile_texture = TEXTURE_MAPPINGS[tile]
                enviorment['window'].blit(tile_texture, (x * TILE_SIZE - startX * TILE_SIZE, y * TILE_SIZE - startY * TILE_SIZE))

        # draw the player relative to the map as a red square
        pygame.draw.rect(enviorment['window'], (255, 0, 0), (self.player_pos[0] * TILE_SIZE - startX * TILE_SIZE, self.player_pos[1] * TILE_SIZE - startY * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # draw the selected tile, along with if it's reachable/valid
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + startX * TILE_SIZE, mouse_pos[1] + startY * TILE_SIZE)
        mouse_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)
        # red if not reachable, white if reachable (5 from player and in the map)
        if mouse_pos[0] < 0 or mouse_pos[0] >= len(map[0]) or mouse_pos[1] < 0 or mouse_pos[1] >= len(map) or Util.distance(self.player_pos, mouse_pos) > 5:
            color = (255, 0, 0)
        else:
            color = (255, 255, 255)

        pygame.draw.rect(enviorment['window'], color, (mouse_pos[0] * TILE_SIZE - startX * TILE_SIZE, mouse_pos[1] * TILE_SIZE - startY * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        
        super().draw(enviorment) # so components can draw themselves on top of the map

    def onEvent(self, event: pygame.event.Event):
        super().onEvent(event) # so components can still handle events
        if self.paused:
            return
        
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            if event.key == pygame.K_ESCAPE:
                self.paused = True
                self.paused_overlay = PauseMenu(self.size, self.enviorment)
                self.enviorment['overlays'].append(self.paused_overlay)
                return
        
        if event.type == pygame.KEYUP:
            self.keys_pressed[event.key] = False