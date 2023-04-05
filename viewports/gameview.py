import pygame, math, time

from components import *
from componentsystem import Viewport
from game.invsystem import HotbarComponent
from game.minimap import MiniMap
from game.particlesystem import ParticleDisplay
from game.savemanager import SaveGame
from game.tiles import Tiles
from game.world import TEXTURE_MAPPINGS, TILE_SIZE
from game.keybinding import Bindings
from myenvironment import Environment
from utils import Util
from viewports.pausemenu import PauseMenu

# 1 one day in game is 20 minutes irl
REAL2GAME = (1 / 60 * 20) # 1 real second is 20 game seconds

class GameView(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment,
                 save: SaveGame = None):
        super().__init__(size, enviorment)
        self.save: SaveGame = save
        if self.save == None: raise Exception("No save file specified")
        self.theme = None # disable automatic themeing

        self.paused: bool = False
        self.paused_overlay: Viewport = None

        self.player_pos: tuple[int, int] = (self.save.save_data['player']['x'], self.save.save_data['player']['y'])
        self.player_velocity: tuple[int, int] = [0, 0]
        self.keys_pressed: dict[int, bool] = {}

        self.game_time: float = self.save.save_data['game_time']
        self.last_time_update: float = time.time()

        self.player_health: int = self.save.save_data['player']['health']
        self.player_max_health: int = self.save.save_data['player']['max_health']
        self.player_max_stamina: int = self.save.save_data['player']['max_stamina']
        self.player_stamina = self.player_max_stamina // 4 # spawn with 1/4 stamina

        self.player_xp = self.save.save_data['player']['xp']

        self.day_count: int = self.save.save_data['day_count']

        self.particle_displays: list[ParticleDisplay] = []

        self.setup()
    
    def setup(self):
        # FPS display
        self.FPS_DISPLAY = TextDisplay(location=(10, 210), text="FPS: ???", color=(255, 255, 255))
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.FPS_DISPLAY)

        # Location display
        self.LOC_DISPLAY = TextDisplay(location=(90, 210), text="Location: ???", color=(255, 255, 255))
        self.LOC_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.LOC_DISPLAY)

        # Time display
        self.TIME_DISPLAY = TextDisplay(location=(10, 230), text="Time: ???", color=(255, 255, 255))
        self.TIME_DISPLAY._LAST_UPDATE_FRAME = 0
        self.registerComponent(self.TIME_DISPLAY)

        # Game stuff
        self.hotbar = HotbarComponent(parent=self)
        self.registerComponent(self.hotbar)

        # Health display
        self.HEALTH_DISPLAY = ProgressBar(location=(5, self.size[1] - 32), size=(175, 20), max_value=self.player_max_health, border_color = (0, 0, 0), border_radius=4)
        self.registerComponent(self.HEALTH_DISPLAY)

        # Stamina display
        self.STAMINA_DISPLAY = ProgressBar(location=(5, self.size[1] - 32 - 24), size=(175, 20), max_value=self.player_max_stamina, border_color = (0, 0, 0), bar_color=(0, 0, 255), border_radius=4)
        self.registerComponent(self.STAMINA_DISPLAY)

        # XP display, thin and above the hotbar
        self.XP_DISPLAY = ProgressBar(location=(self.hotbar.location[0], self.hotbar.location[1] - 14), size=(self.hotbar.size[0] + 33, 10), max_value=100, border_color = (0, 0, 0), bar_color=(154, 66, 205), border_radius=4)
        self.registerComponent(self.XP_DISPLAY)

        # XP level display, above the XP display in the middle
        self.XP_LEVEL_DISPLAY = TextDisplay(location=(self.size[0] // 2 - (DEFAULT_FONT.size("???")[0] // 2), self.XP_DISPLAY.location[1] - 24), text="???", color=(255, 255, 255))
        self.registerComponent(self.XP_LEVEL_DISPLAY)

        self.minimap = MiniMap(parent=self)
        self.registerComponent(self.minimap)

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)
            
    def canMove(self, dir: int, speed: int) -> bool:
        # forward, backward, left, right
        return True
    
    def doGameLogic(self, environment: dict):
        speed = 0.01 * environment['time_delta']
        self.player_velocity = [0, 0]
        if self.keys_pressed.get(Bindings.get("FORWARD"), False):
            self.player_velocity[1] = -speed
        if self.keys_pressed.get(Bindings.get("BACKWARD"), False):
            self.player_velocity[1] = speed
        if self.keys_pressed.get(Bindings.get("LEFT"), False):
            self.player_velocity[0] = -speed
        if self.keys_pressed.get(Bindings.get("RIGHT"), False):
            self.player_velocity[0] = speed

        if self.keys_pressed.get(Bindings.get("SPRINT"), False) and (self.player_velocity[0] != 0 or self.player_velocity[1] != 0):
            if self.player_stamina - 0.02 * environment['time_delta'] > 0:
                self.player_velocity[0] *= 2
                self.player_velocity[1] *= 2
                self.player_stamina -= 0.03 * environment['time_delta']

        # make diagonal movement look less like teleporting
        if self.player_velocity[0] != 0 and self.player_velocity[1] != 0:
            self.player_velocity[0] /= math.sqrt(2)
            self.player_velocity[1] /= math.sqrt(2)

        # update player position
        self.player_pos = (self.player_pos[0] + self.player_velocity[0], self.player_pos[1] + self.player_velocity[1])        

        # update save data
        self.save.save_data['player']['x'] = self.player_pos[0]
        self.save.save_data['player']['y'] = self.player_pos[1]

        # regenerate stamina if below max
        if self.player_stamina < self.player_max_stamina:
            self.player_stamina += 0.01 * environment['time_delta']
            self.player_stamina = min(self.player_max_stamina, self.player_stamina)

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
            self.LOC_DISPLAY.setText(f"({self.player_pos[0]:.0f}, {self.player_pos[1]:.0f})")
        if time.time() - self.TIME_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.TIME_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.TIME_DISPLAY.setText(f"Time: {Util.gameTimeToNice(self.game_time)} - Day {self.day_count}")

            # update the game time
            timeChange = time.time() - self.last_time_update
            self.game_time += REAL2GAME * timeChange
            self.last_time_update = time.time()
            
            if self.game_time > 1501: 
                self.game_time = 60
                self.day_count += 1
                self.save.save_data['day_count'] = self.day_count
            self.save.save_data['game_time'] = self.game_time
        
        self.HEALTH_DISPLAY.value  = self.player_health
        self.STAMINA_DISPLAY.value = self.player_stamina
        self.XP_DISPLAY.value      = self.player_xp % 100
        self.XP_LEVEL_DISPLAY.setText(str(self.player_xp // 100))
        self.XP_LEVEL_DISPLAY.location = (self.size[0] // 2 - (DEFAULT_FONT.size(str(self.player_xp // 100))[0] // 2), self.XP_DISPLAY.location[1] - 24)

        self.enviorment['window'].fill((0, 0, 0))

        # draw the map
        map_data: list[list[int]] = self.save.save_data['world']['map_data']

        # it should be centered on the player
        VIEW_WIDTH = self.size[0]
        VIEW_HEIGHT = self.size[1]

        startX = int(self.player_pos[0]) - (VIEW_WIDTH // TILE_SIZE) // 2
        startY = int(self.player_pos[1]) - (VIEW_HEIGHT // TILE_SIZE) // 2

        # calculate the visible tile range
        minX = max(startX, 0)
        maxX = min(startX + (VIEW_WIDTH // TILE_SIZE) + 1, len(map_data[0]))
        minY = max(startY, 0)
        maxY = min(startY + (VIEW_HEIGHT // TILE_SIZE) + 1, len(map_data))

        # draw only the visible tiles
        for y in range(minY, maxY):
            for x in range(minX, maxX):
                tile = map_data[y][x]
                if not tile:
                    tile = 1

                tile_texture = TEXTURE_MAPPINGS[tile]
                tile_pos = (x * TILE_SIZE - startX * TILE_SIZE, y * TILE_SIZE - startY * TILE_SIZE)
                self.enviorment['window'].blit(tile_texture, tile_pos)

        # draw the player in the middle of the screen
        pygame.draw.rect(enviorment['window'], (255, 0, 0), (VIEW_WIDTH // 2 - TILE_SIZE // 2, VIEW_HEIGHT // 2 - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE))

        # draw the selected tile, along with if it's reachable/valid
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + startX * TILE_SIZE, mouse_pos[1] + startY * TILE_SIZE)
        mouse_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)
        # red if not reachable, white if reachable (5 from player and in the map)
        if mouse_pos[0] < 0 or mouse_pos[0] >= len(map_data[0]) or mouse_pos[1] < 0 or mouse_pos[1] >= len(map_data) or Util.distance(self.player_pos, mouse_pos) > 5:
            color = (255, 0, 0)
        else:
            color = (255, 255, 255)

        pygame.draw.rect(enviorment['window'], color, (mouse_pos[0] * TILE_SIZE - startX * TILE_SIZE, mouse_pos[1] * TILE_SIZE - startY * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        
        for particle_disp in self.particle_displays:
            particle_disp.draw(enviorment['window'], delta_time = enviorment['time_delta'])

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