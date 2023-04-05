import pygame

import game.particlesystem as pSys
from componentsystem import Component
from game.keybinding import Bindings
from game.tiles import Tiles
from game.world import TEXTURE_MAPPINGS, TILE_SIZE, TileIDS
from utils import Util


class Config:
    # Visual
    SLOT_SIZE: int = 48
    ITEM_SIZE: int = 48 - 8 # 4px padding on each side
    BREAK_COLOR: pSys.Color = pSys.Color((70, 66, 38), mod_r=40)

    # Gameplay
    STACK_SIZE: int = 250

class Item:
    def __init__(self, item_id: int, count: int, texture: pygame.Surface):
        self.item_id = item_id
        self.count   = count
        self.texture = pygame.transform.scale(texture, (Config.ITEM_SIZE, Config.ITEM_SIZE)) # just in case

class HotbarComponent(Component):
    def __init__(self, parent):
        self.parent = parent
        location = (parent.size[0] // 2 - Config.SLOT_SIZE * 9 // 2, parent.size[1] - (Config.SLOT_SIZE + 10)) # 10px from the bottom
        super().__init__(location=location, size=(Config.SLOT_SIZE * 9, Config.SLOT_SIZE)) # the size shouldn't really matter
        self.EVENT_SYSTEM_HOOKED = True

        self._items = []
        for item_id, item_count in self.parent.save.save_data['player']['inventory']:
            self._items.append(Item(item_id, item_count, TEXTURE_MAPPINGS[item_id]))

        self._keybind_map = [f"SLOT_{i + 1}" for i in range(len(self._items))]
        self._selected_slot = 0
        self._breaking_power = 9

        self.SLOT_SPACING = 4 # distance between slots

        self.breaking_percent = 0
        self.breaking = False
        self.breaking_tile = None
        self.real_tile = None

        self.count_font = pygame.font.SysFont("Arial", 16)

    def addToInventory(self, item: Item):
        # check if the item is already in the inventory
        for i in range(len(self._items)):
            if self._items[i] and self._items[i].item_id == item.item_id:
                if self._items[i].count + item.count <= Config.STACK_SIZE:
                    self._items[i].count += item.count
                    return

        # if not, find an empty slot
        for i in range(len(self._items)):
            if not self._items[i] or self._items[i].item_id == 0:
                self._items[i] = item
                return
        
        # TODO: Drop the item on the ground when we have support for dropped items

    def draw(self, surface: pygame.Surface, enviorment: dict):
        for i in range(len(self._items)):
            pygame.draw.rect(surface, (255, 255, 255), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), border_radius=(4 if i == self._selected_slot else 0))
            # draw item
            if self._items[i] and self._items[i].item_id != 0:
                surface.blit(self._items[i].texture, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 4, self.location[1] + 4))
                # draw count
                if self._items[i].count > 1:
                    count_surface = self.count_font.render(str(self._items[i].count), True, (255, 255, 255))
                    surface.blit(count_surface, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 8, self.location[1] + 8))
            
            if self._selected_slot == i:
                pygame.draw.rect(surface, (0, 0, 0), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), 2, border_radius=4)

        if self.breaking:
            selected_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player.location, self.parent.size, TILE_SIZE)
            if selected_tile != self.real_tile:
                self.breaking = False
                self.breaking_percent = 0

            pygame.draw.rect(surface, (255, 0, 0), (self.breaking_tile[0] * TILE_SIZE, self.breaking_tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
            pygame.draw.rect(surface, (255, 0, 0), (self.breaking_tile[0] * TILE_SIZE, self.breaking_tile[1] * TILE_SIZE, TILE_SIZE * self.breaking_percent / 100, TILE_SIZE ))
            
            tile = Tiles.getTile(self.parent.save.getTile(self.real_tile[0], self.real_tile[1]))

            self.breaking_percent += Tiles.calculateHitPercent(self._breaking_power, tile.breaking_power, tile.durability)

            if self.breaking_percent >= 100 and self.parent.player.stamina - Util.calculateStaminaCost(self._breaking_power) >= 0:
                self.parent.player.stamina -= Util.calculateStaminaCost(self._breaking_power)
                self.parent.player.xp += 5 * self.parent.save.save_data['player']['xp_multiplier']
                self.parent.save.save_data['player']['xp'] = self.parent.player.xp
                self.breaking = False
                self.breaking_percent = 0

                if tile.drops:
                    for drop in tile.drops:
                        self.addToInventory(Item(drop[0], drop[1], TEXTURE_MAPPINGS[drop[0]]))
                else:
                    self.addToInventory(Item(tile.id, 1, pygame.image.load(tile.texture)))

                self.parent.save.setTile(self.real_tile[0], self.real_tile[1], TileIDS.GRASS)
                self.breaking_tile = None
                self.save()

                # Particles
                p = pSys.ParticleDisplay(start=pygame.mouse.get_pos(), color=Config.BREAK_COLOR, 
                                         shape=pSys.Shape.RANDOM_POLYGON, count=200,
                                         speed=10, lifetime=200, size=1)
                self.parent.particle_displays.append(p)
    
    def save(self):
        self.parent.save.save_data['player']['inventory'] = [[0, 0] for i in range(9)]
        for item in self._items:
            if item:
                self.parent.save.save_data['player']['inventory'][self._items.index(item)] = [item.item_id, item.count]
            else:
                self.parent.save.save_data['player']['inventory'][self._items.index(item)] = [0, 0]
            
    def onEvent(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            for i in range(len(self._keybind_map)):
                if pygame.key.get_pressed()[pygame.K_LSHIFT] and Bindings.check(event, self._keybind_map[i]):
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
            selected_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player.location, self.parent.size, TILE_SIZE)
            if Util.distance(selected_tile, self.parent.player.location) > 5:
                return
            if event.button == 1:
                if Util.calculateStaminaCost(self._breaking_power) > self.parent.player.stamina:
                    p = pSys.ParticleDisplay(start=pygame.mouse.get_pos(), color=Config.BREAK_COLOR, 
                                         shape=pSys.Shape.RANDOM_POLYGON, count=200,
                                         speed=10, lifetime=200, size=1)
                    self.parent.particle_displays.append(p)

                else:
                    self.real_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player.location, self.parent.size, TILE_SIZE)
                    tile = Tiles.getTile(self.parent.save.getTile(self.real_tile[0], self.real_tile[1]))
                    if tile.breakable:
                        self.breaking = True
                        self.breaking_percent = 0
                        self.breaking_tile = (event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE)

            # place block
            elif event.button == 3:
                selected_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player.location, self.parent.size, TILE_SIZE)
                if self._items[self._selected_slot] and self.parent.save.getTile(selected_tile[0], selected_tile[1]) == TileIDS.GRASS:
                    self.parent.save.setTile(selected_tile[0], selected_tile[1], self._items[self._selected_slot].item_id)
                    self._items[self._selected_slot].count -= 1
                    if self._items[self._selected_slot].count <= 0:
                        self._items[self._selected_slot] = None
                    self.save()
            
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