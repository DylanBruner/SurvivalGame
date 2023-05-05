import math, pygame, os, time, json
from game.keybinding import Bindings
from game.world import TILE_SIZE
from utils import Util

CHARACTERS = list(os.listdir("data/assets/character/characters_pack_extended/Heroes"))

class Player:
    def __init__(self, save_data: dict):
        self.max_stamina = save_data['player']['max_stamina']
        self.stamina     = self.max_stamina // 4
        self.max_health  = save_data['player']['max_health']
        self.health      = save_data['player']['health']

        self.xp          = save_data['player']['xp']
        self.coins       = save_data['player']['coins']
        self.location    = [save_data['player']['x'], save_data['player']['y']]
        self.alive       = True

        self.freeze      = False

        self.velocity      = [0, 0]
        self.selected_tile = [None, None]

        # Visuals ===============================
        self.ANIMATION_DELAY = 200 # how many milliseconds between each frame of animation
        with open('data/config/settings.json', 'r') as f:
            self.character = CHARACTERS[json.load(f)['player']['selected_character']]
        self.imageSize  = (24, 32)
        self.playerSize = (self.imageSize[0] * 2, self.imageSize[1] * 2)
        
        # 3x4 spritesheet
        spritesheet = pygame.image.load("data/assets/character/characters_pack_extended/Heroes/" + self.character)
        spritesheet.set_colorkey((0, 117, 117))
        self.images = {
            "back_walk_1": spritesheet.subsurface(pygame.Rect(0, 0, *self.imageSize)),
            "back_walk_2": spritesheet.subsurface(pygame.Rect(24, 0, *self.imageSize)),
            "back_walk_3": spritesheet.subsurface(pygame.Rect(48, 0, *self.imageSize)),
            "right_walk_1": spritesheet.subsurface(pygame.Rect(0, 32, *self.imageSize)),
            "right_walk_2": spritesheet.subsurface(pygame.Rect(24, 32, *self.imageSize)),
            "right_walk_3": spritesheet.subsurface(pygame.Rect(48, 32, *self.imageSize)),
            "front_walk_1": spritesheet.subsurface(pygame.Rect(0, 64, *self.imageSize)),
            "front_walk_2": spritesheet.subsurface(pygame.Rect(24, 64, *self.imageSize)),
            "front_walk_3": spritesheet.subsurface(pygame.Rect(48, 64, *self.imageSize)),
            "left_walk_1": spritesheet.subsurface(pygame.Rect(0, 96, *self.imageSize)),
            "left_walk_2": spritesheet.subsurface(pygame.Rect(24, 96, *self.imageSize)),
            "left_walk_3": spritesheet.subsurface(pygame.Rect(48, 96, *self.imageSize)),
        }
        
        for key in self.images: self.images[key] = pygame.transform.scale(self.images[key], (self.images[key].get_width() * 2, self.images[key].get_height() * 2))
        for key in self.images: self.images[key].set_colorkey((0, 117, 117))

        # Animation Stuff ===============================
        self.selected_image = "front_walk_1"
        self.facing = "front"
        self.last_animation = time.time()
        self.animation_index = 1
        self.sprinting = False
        self.idle = True

    @Util.MonkeyUtils.autoErrorHandling
    def save(self, parent: object):
        parent.save.save_data['player']['x'] = self.location[0]
        parent.save.save_data['player']['y'] = self.location[1]
        parent.save.save_data['player']['health'] = self.health
        parent.save.save_data['player']['xp'] = self.xp
        parent.save.save_data['player']['max_health'] = self.max_health
        parent.save.save_data['player']['max_stamina'] = self.max_stamina
        parent.save.save_data['player']['coins'] = self.coins
    
    @Util.MonkeyUtils.autoErrorHandling
    def tick(self, keys_pressed: dict, environment: dict) -> None:
        if self.freeze: return
        self.parent = environment['viewport']
        speed = 0.001 * environment['time_delta'] * 40 #TEMP SPEEDUP
        self.velocity = [0, 0]
        if keys_pressed.get(Bindings.get("LEFT"), False):
            self.velocity[0] = -speed
            self.facing = "left"
        if keys_pressed.get(Bindings.get("RIGHT"), False):
            self.velocity[0] = speed
            self.facing = "right"
        if keys_pressed.get(Bindings.get("FORWARD"), False):
            self.velocity[1] = -speed
            self.facing = "back"
        if keys_pressed.get(Bindings.get("BACKWARD"), False):
            self.velocity[1] = speed
            self.facing = "front"
        
        self.idle = (self.velocity[0] == 0 and self.velocity[1] == 0)

        if keys_pressed.get(Bindings.get("SPRINT"), False) and (self.velocity[0] != 0 or self.velocity[1] != 0):
            if self.stamina - 0.02 * environment['time_delta'] > 0:
                self.sprinting = True
                self.velocity[0] *= 3
                self.velocity[1] *= 3
                self.stamina -= 0.007 * environment['time_delta']
            else: self.sprinting = False
        else: self.sprinting = False

        # make diagonal movement look less like teleporting
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            self.velocity[0] /= math.sqrt(2)
            self.velocity[1] /= math.sqrt(2)

        # update player position
        self.location = (self.location[0] + self.velocity[0], self.location[1] + self.velocity[1])

        xLimit = len(self.parent.save.save_data['world']['map_data'][0]) - 1
        yLimit = len(self.parent.save.save_data['world']['map_data']) - 1.4
        self.location = (max(0, min(self.location[0], xLimit)), max(0.2, min(self.location[1], yLimit)))

        # regenerate stamina if below max
        if self.stamina < self.max_stamina and not self.sprinting:
            self.stamina += 0.01 * environment['time_delta']
            self.stamina = min(self.max_stamina, self.stamina)

    @Util.MonkeyUtils.autoErrorHandling
    def handleAnimations(self) -> None:
        if self.idle: return
        if not self.selected_image.startswith(self.facing):
            self.selected_image = self.facing + "_walk_1"
            self.animation_index = 1
            self.last_animation = time.time()
            return
        
        if time.time() - self.last_animation > (self.ANIMATION_DELAY if not self.sprinting else self.ANIMATION_DELAY // 2) / 1000:
            self.animation_index += 1
            if self.animation_index > 3: self.animation_index = 1
            self.selected_image = self.facing + "_walk_" + str(self.animation_index)
            self.last_animation = time.time()

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface) -> None:
        self.handleAnimations()

        surface.blit(self.images[self.selected_image], (surface.get_width() / 2 - self.images[self.selected_image].get_width() / 2,
                                                        surface.get_height() / 2 - self.images[self.selected_image].get_height() / 2))