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
from game.player import Player
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

        self.player_velocity: tuple[int, int] = [0, 0]
        self.keys_pressed: dict[int, bool] = {}

        self.game_time: float = self.save.save_data['game_time']
        self.last_time_update: float = time.time()

        self.player = Player()
        self.player.max_health  = self.save.save_data['player']['max_health']
        self.player.health      = self.save.save_data['player']['health']
        self.player.max_stamina = self.save.save_data['player']['max_stamina']
        self.player.stamina     = self.save.save_data['player']['max_stamina'] // 4
        self.player.xp          = self.save.save_data['player']['xp']
        self.player.location    = [self.save.save_data['player']['x'], self.save.save_data['player']['y']]

        self.day_count: int = self.save.save_data['day_count']

        self.particle_displays: list[ParticleDisplay] = []

        self.setup()
    
    def setup(self):
        self.FPS_DISPLAY = TextDisplay(location=(10, 210), text="FPS: ???", color=(255, 255, 255))
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0

        self.LOC_DISPLAY = TextDisplay(location=(90, 210), text="Location: ???", color=(255, 255, 255))
        self.LOC_DISPLAY._LAST_UPDATE_FRAME = 0

        self.TIME_DISPLAY = TextDisplay(location=(10, 230), text="Time: ???", color=(255, 255, 255))
        self.TIME_DISPLAY._LAST_UPDATE_FRAME = 0

        self.hotbar = HotbarComponent(parent=self)
        self.HEALTH_DISPLAY = ProgressBar(location=(5, self.size[1] - 32), size=(175, 20), max_value=self.player.max_health, border_color = (0, 0, 0), border_radius=4)
        self.STAMINA_DISPLAY = ProgressBar(location=(5, self.size[1] - 32 - 24), size=(175, 20), max_value=self.player.max_stamina, border_color = (0, 0, 0), bar_color=(0, 0, 255), border_radius=4)
        self.XP_DISPLAY = ProgressBar(location=(self.hotbar.location[0], self.hotbar.location[1] - 14), size=(self.hotbar.size[0] + 33, 10), max_value=100, border_color = (0, 0, 0), bar_color=(154, 66, 205), border_radius=4)
        self.XP_LEVEL_DISPLAY = TextDisplay(location=(self.size[0] // 2 - (DEFAULT_FONT.size("???")[0] // 2), self.XP_DISPLAY.location[1] - 24), text="???", color=(255, 255, 255))

        self.minimap = MiniMap(parent=self)

        self.registerComponents([
            self.FPS_DISPLAY, self.LOC_DISPLAY, self.TIME_DISPLAY,
            self.hotbar, self.HEALTH_DISPLAY, self.STAMINA_DISPLAY,
            self.XP_DISPLAY, self.XP_LEVEL_DISPLAY, self.minimap
        ])

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)
            
    def canMove(self, dir: int, speed: int) -> bool:
        # forward, backward, left, right
        return True
    
    def doGameLogic(self, environment: dict):
        speed = 0.008 * environment['time_delta']
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
            if self.player.stamina - 0.02 * environment['time_delta'] > 0:
                self.player_velocity[0] *= 2
                self.player_velocity[1] *= 2
                self.player.stamina -= 0.03 * environment['time_delta']

        # make diagonal movement look less like teleporting
        if self.player_velocity[0] != 0 and self.player_velocity[1] != 0:
            self.player_velocity[0] /= math.sqrt(2)
            self.player_velocity[1] /= math.sqrt(2)

        # update player position
        self.player.location = (self.player.location[0] + self.player_velocity[0], self.player.location[1] + self.player_velocity[1])        

        # update save data
        self.save.save_data['player']['x'] = self.player.location[0]
        self.save.save_data['player']['y'] = self.player.location[1]

        # regenerate stamina if below max
        if self.player.stamina < self.player.max_stamina:
            self.player.stamina += 0.01 * environment['time_delta']
            self.player.stamina = min(self.player.max_stamina, self.player.stamina)

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
            self.LOC_DISPLAY.setText(f"({self.player.location[0]:.0f}, {self.player.location[1]:.0f})")
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
        
        self.HEALTH_DISPLAY.value  = self.player.health
        self.STAMINA_DISPLAY.value = self.player.stamina
        self.XP_DISPLAY.value      = self.player.xp % 100
        self.XP_LEVEL_DISPLAY.setText(str(self.player.xp // 100))
        self.XP_LEVEL_DISPLAY.location = (self.size[0] // 2 - (DEFAULT_FONT.size(str(self.player.xp // 100))[0] // 2), self.XP_DISPLAY.location[1] - 24)

        self.enviorment['window'].fill((0, 0, 0))

        # draw the map
        map_data: list[list[int]] = self.save.save_data['world']['map_data']

        # Define the size of the visible area around the player
        visible_width = self.size[0] // TILE_SIZE + 32
        visible_height = self.size[1] // TILE_SIZE + 32

        # Get the player's position
        player_x, player_y = self.player.location[0] + 16, self.player.location[1] + 16

        # Calculate the bounds of the visible area
        left_plane = player_x - visible_width // 2
        right_plane = left_plane + visible_width
        bottom_plane = player_y - visible_height // 2
        top_plane = bottom_plane + visible_height

        # Iterate only over the tiles that are visible
        for x in range(int(left_plane), int(right_plane)):
            for y in range(int(bottom_plane), int(top_plane)):
                # Check if the tile is within the bounds of the map
                if x >= 0 and x < len(map_data) and y >= 0 and y < len(map_data[x]):
                    texture = TEXTURE_MAPPINGS[map_data[x][y]]
                    if texture is not None:
                        # Calculate the position of the tile on the screen
                        screen_x = (x - left_plane) * TILE_SIZE
                        screen_y = (y - bottom_plane) * TILE_SIZE
                        self.enviorment['window'].blit(texture, (screen_x, screen_y))
                        # draw black border around the tile
                        pygame.draw.rect(self.enviorment['window'], (0, 0, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

                        # check if the mouse is hovering over the tile
                        if pygame.mouse.get_pos()[0] >= screen_x and pygame.mouse.get_pos()[0] <= screen_x + TILE_SIZE and pygame.mouse.get_pos()[1] >= screen_y and pygame.mouse.get_pos()[1] <= screen_y + TILE_SIZE:
                            self.player.selected_tile = (x, y)

                            color = (255, 0, 0) if Util.distance(self.player.selected_tile, self.player.location) > 5 else (255, 255, 255)
                            pygame.draw.rect(self.enviorment['window'], color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)


        # draw the player as a red rect
        pygame.draw.rect(self.enviorment['window'], (255, 0, 0), (self.size[0] // 2 - 16, self.size[1] // 2 - 16, 32, 32), 1)
        # text = DEFAULT_FONT.render(f"({self.player.selected_tile[0]}, {self.player.selected_tile[1]})", True, (255, 255, 255))
        # self.enviorment['window'].blit(text, (self.size[0] // 2 - text.get_width() // 2, self.size[1] // 2 - text.get_height() // 2))
        
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