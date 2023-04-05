import time

import pygame

from components import *
from componentsystem import Viewport
from game.invsystem import HotbarComponent
from game.minimap import MiniMap
from game.savemanager import SaveGame
from game.tiles import Tiles
from game.world import TEXTURE_MAPPINGS, TILE_SIZE, TileIDS
from myenvironment import Environment
from utils import Util
from viewports.pausemenu import PauseMenu

# 1 one day in game is 20 minutes irl
REAL2GAME = (1 / 60 * 20) * 200 # 1 real second is 20 game seconds

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
        self.move_pos: tuple[int, int] = (0, 0)
        self.keys_pressed: dict[int, bool] = {}

        self.game_time: float = self.save.save_data['game_time']
        self.last_time_update: float = time.time()

        self.setup()
    
    def setup(self):
        # FPS display
        self.FPS_DISPLAY = TextDisplay(location=(10, 210), text="FPS: ???", color=(255, 255, 255))
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.FPS_DISPLAY)

        # Location display
        self.LOC_DISPLAY = TextDisplay(location=(80, 210), text="Location: ???", color=(255, 255, 255))
        self.LOC_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.LOC_DISPLAY)

        # Time display
        self.TIME_DISPLAY = TextDisplay(location=(10, 230), text="Time: ???", color=(255, 255, 255))
        self.TIME_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.TIME_DISPLAY)

        # Game stuff
        self.hotbar = HotbarComponent(parent=self)
        self.registerComponent(self.hotbar)

        self.minimap = MiniMap(parent=self)
        self.registerComponent(self.minimap)
            
    def canMove(self, dir: int, speed: int) -> bool:
        # forward, backward, left, right
        projected_pos = None
        if dir == 0:
            projected_pos = (self.move_pos[0], self.move_pos[1] - speed)
        elif dir == 1:
            projected_pos = (self.move_pos[0], self.move_pos[1] + speed)
        elif dir == 2:
            projected_pos = (self.move_pos[0] - speed, self.move_pos[1])
        elif dir == 3:
            projected_pos = (self.move_pos[0] + speed, self.move_pos[1])
        else:
            raise Exception(f"Invalid direction: {dir}")
        projected_pos = (int(projected_pos[0]), int(projected_pos[1]))

        # if projected_pos is out of bounds, return False
        if projected_pos[0] < 0 or projected_pos[0] >= len(self.save.save_data['world']['map_data'][0]):
            return False
        if projected_pos[1] < 0 or projected_pos[1] >= len(self.save.save_data['world']['map_data']):
            return False

        tileAt = self.save.save_data['world']['map_data'][projected_pos[1]][projected_pos[0]]        

        return not Tiles.getTile(tileAt).collidable
    
    def doGameLogic(self, enviorment: dict):
        # handle key presses
        speed = 0.05 * enviorment['time_delta']
        if self.keys_pressed.get(pygame.K_a, False) and self.canMove(2, speed):
            self.move_pos = (self.move_pos[0] - speed, self.move_pos[1])
        if self.keys_pressed.get(pygame.K_d, False) and self.canMove(3, speed):
            self.move_pos = (self.move_pos[0] + speed, self.move_pos[1])
        if self.keys_pressed.get(pygame.K_w, False) and self.canMove(0, speed):
            self.move_pos = (self.move_pos[0], self.move_pos[1] - speed)
        if self.keys_pressed.get(pygame.K_s, False) and self.canMove(1, speed):
            self.move_pos = (self.move_pos[0], self.move_pos[1] + speed)
        
        # limit the player to the map
        self.player_pos = (max(0, min(int(self.move_pos[0]), len(self.save.save_data['world']['map_data'][0]) - 1)),
                           max(0, min(int(self.move_pos[1]), len(self.save.save_data['world']['map_data']) - 1)))
            
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
        if time.time() - self.LOC_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.LOC_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.LOC_DISPLAY.setText(f"({self.player_pos[0]}, {self.player_pos[1]})")
        if time.time() - self.TIME_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.TIME_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.TIME_DISPLAY.setText(f"Time: {Util.gameTimeToNice(self.game_time)}")

            # update the game time
            timeChange = time.time() - self.last_time_update
            self.game_time += REAL2GAME * timeChange
            self.last_time_update = time.time()
            
            if self.game_time > 1501: self.game_time = 60

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

VIEWPORT_CLASS = GameView