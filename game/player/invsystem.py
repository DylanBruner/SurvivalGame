import pygame

import game.display.particlesystem as pSys
from components.componentsystem import Component
from game.misc.keybinding import Bindings
from game.player.playerstorage import PlayerStorage
from game.save.tiles import Tiles
from game.save.world import TEXTURE_MAPPINGS, TileIDS
from util.utils import Util
from game.misc.sounds import Sounds
from _types.item import Item

class Config:
    # Visual
    SLOT_SIZE: int = 42
    ITEM_SIZE: int = 42 - 8 # 4px padding on each side
    BREAK_COLOR: pSys.Color = pSys.Color((70, 66, 38), mod_r=40)

    # Gameplay
    STACK_SIZE: int = 250

class HotbarComponent(Component):
    def __init__(self, parent):
        self.parent = parent
        location = (parent.size[0] // 2 - Config.SLOT_SIZE * 9 // 2, parent.size[1] - (Config.SLOT_SIZE + 10)) # 10px from the bottom
        super().__init__(location=location, size=(Config.SLOT_SIZE * 9, Config.SLOT_SIZE)) # the size shouldn't really matter
        self.EVENT_SYSTEM_HOOKED = True
        self.priority = 1

        self._items = self.parent.save.save_data['player']['inventory']
        # for item_id, item_count in self.parent.save.save_data['player']['inventory']:
            # self._items.append(Item(item_id, item_count, (Config.ITEM_SIZE, Config.ITEM_SIZE)))
   
        self._keybind_map = [f"SLOT_{i + 1}" for i in range(len(self._items))]
        self._selected_slot = 0
        self._breaking_power = 9

        self.SLOT_SPACING = 4 # distance between slots
        self.slotRects: list[pygame.Rect] = [None for _ in range(len(self._items))]

        self.breaking_percent: int = 0
        self.breaking_id: int = None
        self.breaking: bool = False
        self.breaking_tile: list[int, int] = None

        self.count_font = pygame.font.SysFont("Arial", 16)

        self.STORAGE_MENU = PlayerStorage(self.parent)

    @Util.MonkeyUtils.autoErrorHandling
    def addToInventory(self, item: Item):
        # check if the item is already in the inventory
        for i in range(len(self._items)):
            if self._items[i] and self._items[i].item_id == item.item_id:
                if self._items[i].count + item.count <= Config.STACK_SIZE:
                    self._items[i].count += item.count
                    self.save()
                    return

        # if not, find an empty slot
        for i in range(len(self._items)):
            if not self._items[i] or self._items[i].item_id == 0:
                self._items[i] = item
                self.save()
                return
        
        # TODO: Drop the item on the ground when we have support for dropped items

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, environment: dict):
        for i in range(len(self._items)):
            pygame.draw.rect(surface, (255, 255, 255), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), border_radius=(4 if i == self._selected_slot else 0))
            # draw item
            if self._items[i] and self._items[i].item_id != 0:
                surface.blit(TEXTURE_MAPPINGS[self._items[i].item_id], (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 4, self.location[1] + 4))
                # draw count
                if self._items[i].count > 1:
                    count_surface = self.count_font.render(str(self._items[i].count), True, (255, 255, 255))
                    surface.blit(count_surface, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 8, self.location[1] + 8))
            
            self.slotRects[i] = pygame.Rect(self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), 
                                            self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE)

            if self._selected_slot == i:
                pygame.draw.rect(surface, (0, 0, 0), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), 2, border_radius=4)

        if self.STORAGE_MENU.open:
            self.STORAGE_MENU.draw(surface, environment)
            return

        if self.breaking:
            if self.breaking_tile != self.parent.player.selected_tile or self.parent.player.stamina < Util.calculateStaminaCost(self._breaking_power, self.parent.player.xp):
                self.breaking = False
                self.breaking_percent = 0
                self.breaking_tile = None
                self.breaking_id = None
                return
            self.breaking_percent += ((self._breaking_power * 10) / Tiles.getTile(self.breaking_id).durability) * environment['time_delta']

            if self.breaking_percent >= 100:
                Sounds.playSound(Sounds.BLOCK_BREAK)
                self.parent.player.stamina -= Util.calculateStaminaCost(self._breaking_power, self.parent.player.xp)
                self.parent.player.xp += 5 # xp system needs to be worked out
                tile = Tiles.getTile(self.breaking_id)
                if tile:
                    if tile.drops:
                        for drop in tile.drops:
                            self.addToInventory(Item(drop[0], drop[1]))
                    else:
                        self.addToInventory(Item(self.breaking_id, 1))

                self.breaking_percent = 0
                self.breaking = False
                self.breaking_tile = None
                self.breaking_id = None
                self.parent.save.save_data['world']['map_data'][self.parent.player.selected_tile[0]][self.parent.player.selected_tile[1]] = TileIDS.GRASS
                
                p = pSys.ParticleDisplay(start=pygame.mouse.get_pos(), color=Config.BREAK_COLOR, 
                            shape=pSys.Shape.RANDOM_POLYGON, count=125,
                            speed=10, lifetime=200, size=1)
                self.parent.particle_displays.append(p)
                                            
                return

            tile_loc = self.parent.getTileLocation(self.breaking_tile)
            # draw a progress bar that shows how much the player has broken the block
            pygame.draw.rect(surface, (255, 0, 0), (tile_loc[0], tile_loc[1] - 10, Config.SLOT_SIZE * (self.breaking_percent / 150), 5))
    
    @Util.MonkeyUtils.autoErrorHandling
    def save(self):
        self.parent.save.save_data['player']['inventory'] = [[0, 0] for i in range(9)]
        for item in self._items:
            self.parent.save.save_data['player']['inventory'][self._items.index(item)] = item#[item.item_id, item.count]
            # if item:
            # else:
                # self.parent.save.save_data['player']['inventory'][self._items.index(item)] = [0, 0]
    
    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if Bindings.get("INVENTORY") == event.key:
                self.STORAGE_MENU.clearOpenChest()
                self.STORAGE_MENU.open    = not self.STORAGE_MENU.open
                self.parent.player.freeze = self.STORAGE_MENU.open
                if self.STORAGE_MENU.open:
                    self.STORAGE_MENU.onOpen()
                
        if self.STORAGE_MENU.open:
            self.STORAGE_MENU.onEvent(event)
            if event.type == pygame.WINDOWRESIZED:
                self.STORAGE_MENU.setup()
            return
            
        if event.type == pygame.KEYDOWN:
            for i in range(len(self._keybind_map)):
                if pygame.key.get_pressed()[pygame.K_TAB] and Bindings.check(event, self._keybind_map[i]):
                    if self._selected_slot == i: continue
                    item1 = self._items[self._selected_slot]
                    item2 = self._items[i]

                    # if possible merge the items
                    if item1 and item2 and item1.item_id == item2.item_id:
                        if item1.count + item2.count <= Config.STACK_SIZE:
                            item1.count += item2.count
                            self._items[i] = None
                            self.save()
                            return
                    
                    # swap the items
                    self._items[self._selected_slot] = item2
                    self._items[i] = item1
                    self.save()
                elif Bindings.check(event, self._keybind_map[i]):
                    self._selected_slot = i     
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not Util.distance(self.parent.player.selected_tile, self.parent.player.location) > 5:
                tile_id = self.parent.save.save_data['world']['map_data'][self.parent.player.selected_tile[0]][self.parent.player.selected_tile[1]]
                if not self.breaking and Tiles.getTile(tile_id) != None:
                    if Tiles.getTile(tile_id).breakable and self.parent.player.stamina > Util.calculateStaminaCost(self._breaking_power, self.parent.player.xp):
                        self.breaking_tile = self.parent.player.selected_tile

                        self.breaking_percent = 0
                        self.breaking         = True
                        self.breaking_id      = tile_id

            # place block
            elif (event.button == 3 and not Util.distance(self.parent.player.selected_tile, self.parent.player.location) > 5 and
                  (tile_id := self.parent.save.save_data['world']['map_data'][self.parent.player.selected_tile[0]][self.parent.player.selected_tile[1]]) == TileIDS.GRASS):
                
                if tile_id == TileIDS.GRASS or tile_id == TileIDS.EMPTY:
                    if self._items[self._selected_slot].item_id == 0: return
                    if self._items[self._selected_slot]:
                        self.parent.save.save_data['world']['map_data'][self.parent.player.selected_tile[0]][self.parent.player.selected_tile[1]] = self._items[self._selected_slot].item_id
                        self._items[self._selected_slot].count -= 1
                        if self._items[self._selected_slot].count <= 0:
                            self._items[self._selected_slot] = None
                        self.save()

            elif (event.button == 3 and not Util.distance(self.parent.player.selected_tile, self.parent.player.location) > 5 and
                  (tile_id := self.parent.save.save_data['world']['map_data'][self.parent.player.selected_tile[0]][self.parent.player.selected_tile[1]]) == TileIDS.CHEST):
                
                x, y = self.parent.player.selected_tile
                for key, value in self.parent.save.save_data['chests'].items():
                    cx, cy = key.split(',')
                    if str(cy) == str(x) and str(cx) == str(y): # keys are a bit messed up...
                        self.STORAGE_MENU.loadChestContents(self.parent.player.selected_tile)
                        break
                else:
                    # TODO: Maybe fix this
                    # chest wasn't found so create a new one
                    # self.parent.save.save_data['chests'][f'{y},{x}'] = []
                    # self.STORAGE_MENU.loadChestContents(self.parent.player.selected_tile)
                    ...             
            # scroll
            elif event.button == 4:
                self._selected_slot -= 1
                if self._selected_slot < 0:
                    self._selected_slot = len(self._items) - 1
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.breaking:
                    self.breaking = False
                    self.breaking_percent = 0
            
            # scroll
            elif event.button == 5:
                self._selected_slot += 1
                if self._selected_slot >= len(self._items):
                    self._selected_slot = 0