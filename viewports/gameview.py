import time, pygame

from components import *
from componentsystem import Viewport
from game.enemy import Enemy
from game.invsystem import HotbarComponent
from game.minimap import MiniMap
from game.particlesystem import ParticleDisplay
from game.player import Player
from game.savemanager import SaveGame
from game.tiles import Tiles
from game.world import TEXTURE_MAPPINGS, TILE_SIZE
from myenvironment import Environment
from utils import Util
from viewports.pausemenu import PauseMenu
from enemies.testpathfinder import TestPathfinderEnemy

# 1 one day in game is 20 minutes irl
REAL2GAME = (1 / 60 * 20) # 1 real second is 20 game seconds

class Lighting:
    @staticmethod
    def circle(radius: int, color: tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    @staticmethod
    def rect(size: tuple[int, int], color: tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, *size))
        surf.set_colorkey((0, 0, 0))
        return surf

class Images:
    COIN_IMAGE = pygame.image.load("data/assets/coin.png")

class GameView(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment,
                 save: SaveGame = None):
        super().__init__(size, environment)
        self.save: SaveGame = save
        if self.save == None: raise Exception("No save file specified")
        self.theme = None # disable automatic themeing

        self.paused: bool = False
        self.paused_overlay: Viewport = None
        self.keys_pressed: dict[int, bool] = {}

        self.game_time: float = self.save.save_data['game_time']
        self.day_count: int   = self.save.save_data['day_count']
        self.blood_moon: bool = (self.day_count % 7) == 0
        self.last_time_update: float = time.time()

        self.enemies: list[Enemy] = []
        self.player = Player(self.save.save_data)

        self.particle_displays: list[ParticleDisplay] = []
        self.ui_layer: pygame.Surface   = None
        self.game_layer: pygame.Surface = None

        self.setup()
    
    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        self.ui_layer   = pygame.Surface(self.size, pygame.SRCALPHA)
        self.game_layer = pygame.Surface(self.size, pygame.SRCALPHA)

        self.FPS_DISPLAY = TextDisplay(location=(self.size[0] - 80, 10), text="FPS: ???", color=(255, 255, 255))
        self.FPS_DISPLAY._LAST_UPDATE_FRAME = 0

        self.TIME_DISPLAY = TextDisplay(location=(10, 232), text="Time: ???", color=(255, 255, 255))
        self.TIME_DISPLAY._LAST_UPDATE_FRAME = 0

        self.hotbar = HotbarComponent(parent=self)
        self.HEALTH_DISPLAY = ProgressBar(location=(5, self.size[1] - 32), 
                                          size=(175, 20), max_value=self.player.max_health, border_color = (0, 0, 0), 
                                          border_radius=4, text_display=True, text_color=(0, 0, 0))
        
        self.STAMINA_DISPLAY = ProgressBar(location=(5, self.size[1] - 32 - 24), 
                                           size=(175, 20), max_value=self.player.max_stamina, 
                                           border_color = (0, 0, 0), bar_color=(20, 220, 220), border_radius=4, text_display=True, 
                                           text_color=(0, 0, 0))
        
        self.XP_DISPLAY = ProgressBar(location=(self.hotbar.location[0], self.hotbar.location[1] - 14), 
                                      size=(self.hotbar.size[0] + 33, 10), max_value=100, border_color = (0, 0, 0), 
                                      bar_color=(154, 66, 205), border_radius=4)
        
        self.XP_LEVEL_DISPLAY = TextDisplay(location=(self.size[0] // 2 - (DEFAULT_FONT.size("???")[0] // 2), 
                                                      self.XP_DISPLAY.location[1] - 24), text="???", color=(255, 255, 255))

        self.minimap = MiniMap(parent=self)

        # Money display
        self.coin_image = ImageDisplay(location=(8, 212), image=Images.COIN_IMAGE)
        self.coins_display = TextDisplay(location=(36, 212), text="???", color=(255, 255, 255))

        self.registerComponents([
            self.FPS_DISPLAY, self.TIME_DISPLAY, self.hotbar,
            self.HEALTH_DISPLAY, self.STAMINA_DISPLAY,
            self.XP_DISPLAY, self.XP_LEVEL_DISPLAY, self.minimap,
            self.coins_display, self.coin_image
        ])

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

    @Util.MonkeyUtils.autoErrorHandling
    def doGameLogic(self, environment: dict):
        self.player.tick(self.keys_pressed, environment)

        self.save.save_data['player']['x'] = self.player.location[0]
        self.save.save_data['player']['y'] = self.player.location[1]
    
    @Util.MonkeyUtils.autoErrorHandling
    def drawLighting(self):
        # night color
        color = [0, 0, 0]
        if self.game_time < 400:
            color = self.game_time * 0.8, self.game_time * 0.8, self.game_time * 0.8
        elif self.game_time > 1000:
            if self.blood_moon:
                color = [1550 - (self.game_time), (1300 - (self.game_time)), 1300 - (self.game_time)]
            else:
                color = (1450 - (self.game_time)), (1450 - (self.game_time)), (1450 - (self.game_time))
        else:
            color = [255, 255, 255]

        color = [int(max(70, min(255, c))) for c in color]

        surf = Lighting.rect(self.size, color)
        self.game_layer.blit(surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, environment: dict):
        if self.paused:
            if self.paused_overlay.closed:
                self.paused = False
                self.paused_overlay = None
                return
            self.paused_overlay.draw(environment)
            return
        
        self.doGameLogic(environment)

        if time.time() - self.FPS_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.FPS_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.FPS_DISPLAY.setText(f"FPS: {environment['clock'].get_fps():.0f}")
        if time.time() - self.TIME_DISPLAY._LAST_UPDATE_FRAME > 0.05:
            self.TIME_DISPLAY._LAST_UPDATE_FRAME = time.time()
            self.TIME_DISPLAY.setText(f"Time: {Util.gameTimeToNice(self.game_time)} (Day {self.day_count})")

            # update the game time
            timeChange = time.time() - self.last_time_update
            self.game_time += (REAL2GAME * timeChange)
            self.last_time_update = time.time()
            
            if self.game_time > 1501: 
                self.game_time = 60
                self.day_count += 1
                self.save.save_data['day_count'] = self.day_count

                if (self.day_count % 7) == 0 and self.save.save_data['difficulty']['blood_moon']:
                    self.blood_moon = True
                    self.TIME_DISPLAY.color = (255, 0, 0)
                else: 
                    self.blood_moon = False
                    self.TIME_DISPLAY.color = (255, 255, 255)

            self.save.save_data['game_time'] = self.game_time
        
        self.coins_display.setText(f"{self.player.coins:,}")
        
        self.HEALTH_DISPLAY.value  = self.player.health
        self.STAMINA_DISPLAY.value = self.player.stamina
        self.XP_DISPLAY.value      = self.player.xp % 100
        self.XP_LEVEL_DISPLAY.setText(str(self.player.xp // 100))
        self.XP_LEVEL_DISPLAY.location = (self.size[0] // 2 - (DEFAULT_FONT.size(str(self.player.xp // 100))[0] // 2), self.XP_DISPLAY.location[1] - 24)

        self.game_layer.fill((0, 0, 0))
        self.ui_layer.fill((0, 0, 0, 0))

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
                    tile_id = map_data[x][y]
                    texture = TEXTURE_MAPPINGS[tile_id]
                    if texture is not None:
                        # Calculate the position of the tile on the screen
                        screen_x = (x - left_plane) * TILE_SIZE
                        screen_y = (y - bottom_plane) * TILE_SIZE
                        if Tiles.getTile(tile_id).background_id:
                            self.game_layer.blit(TEXTURE_MAPPINGS[Tiles.getTile(tile_id).background_id], (screen_x, screen_y))

                        self.game_layer.blit(texture, (screen_x, screen_y))
                        # draw black border around the tile
                        # pygame.draw.rect(self.game_layer, (0, 0, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

                        # check if the mouse is hovering over the tile
                        if pygame.mouse.get_pos()[0] >= screen_x and pygame.mouse.get_pos()[0] <= screen_x + TILE_SIZE and pygame.mouse.get_pos()[1] >= screen_y and pygame.mouse.get_pos()[1] <= screen_y + TILE_SIZE:
                            self.player.selected_tile = (x, y)

                            color = (255, 0, 0) if Util.distance(self.player.selected_tile, self.player.location) > 5 else (255, 255, 255)
                            pygame.draw.rect(self.ui_layer, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        for enemy in self.enemies:
            if Util.distance(enemy.location, self.player.location) < 100:
                ex = (enemy.location[0] - left_plane) * TILE_SIZE
                ey = (enemy.location[1] - bottom_plane) * TILE_SIZE
                enemy.draw(self.game_layer, environment, (ex, ey))

        self.player.draw(self.game_layer)
        # text = DEFAULT_FONT.render(f"({self.player.selected_tile[0]}, {self.player.selected_tile[1]})", True, (255, 255, 255))
        # self.ui_layer.blit(text, (self.size[0] // 2 - text.get_width() // 2, self.size[1] // 2 - text.get_height() // 2))
        
        for particle_disp in self.particle_displays:
            particle_disp.draw(self.game_layer, delta_time = environment['time_delta'])

        self.components['components'].sort(key = lambda component: component.priority, reverse = False)
        for component in self.components['components']:
            component.draw(self.ui_layer, environment)
        
        if self._customCursorEnabled:
            self.ui_layer.blit(self.customCursor, pygame.mouse.get_pos())

        self.drawLighting()
        
        self.environment['window'].blit(self.game_layer, (0, 0))
        self.environment['window'].blit(self.ui_layer, (0, 0))
    
    @Util.MonkeyUtils.autoErrorHandling
    def getTileLocation(self, loc: tuple[int, int]) -> tuple[int, int]:
        """
        Take a position in the world and return the top left corner of the tile relative to the window
        """
        visible_width = self.size[0] // TILE_SIZE + 32
        visible_height = self.size[1] // TILE_SIZE + 32

        # Get the player's position
        player_x, player_y = self.player.location[0] + 16, self.player.location[1] + 16

        left_plane = player_x - visible_width // 2
        bottom_plane = player_y - visible_height // 2

        return (loc[0] - left_plane) * TILE_SIZE, (loc[1] - bottom_plane) * TILE_SIZE

    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event):
        super().onEvent(event) # so components can still handle events
        if self.paused:
            return
        
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            if event.key == pygame.K_ESCAPE:
                self.paused = True
                self.paused_overlay = PauseMenu(self.size, self.environment)
                self.environment['overlays'].append(self.paused_overlay)
                return
            
            elif event.key == pygame.K_j:
                self.enemies.append(TestPathfinderEnemy((
                    self.player.selected_tile[0],
                    self.player.selected_tile[1]
                ), self))

        if event.type == pygame.KEYUP:
            self.keys_pressed[event.key] = False

VIEWPORT_CLASS = GameView # monkey reloading