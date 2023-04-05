import pygame
from game.tiles import Tiles

from componentsystem import Component
from game.keybinding import Bindings
from game.world import TILE_SIZE, TileIDS
from utils import Util


class Config:
    # Visual
    SLOT_SIZE: int = 48
    ITEM_SIZE: int = 48 - 8 # 4px padding on each side

    # Gameplay
    STACK_SIZE: int = 99

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

        self._items = [None, None, None, None, None, None, None, None, None] # 9 slots
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
            if not self._items[i]:
                self._items[i] = item
                return
        
        # TODO: Drop the item on the ground when we have support for dropped items

    def draw(self, surface: pygame.Surface, enviorment: dict):
        for i in range(len(self._items)):
            pygame.draw.rect(surface, (255, 255, 255), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), border_radius=(4 if i == self._selected_slot else 0))
            # draw item
            if self._items[i]:
                surface.blit(self._items[i].texture, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 4, self.location[1] + 4))
                # draw count
                if self._items[i].count > 1:
                    count_surface = self.count_font.render(str(self._items[i].count), True, (255, 255, 255))
                    surface.blit(count_surface, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 8, self.location[1] + 8))
            
            if self._selected_slot == i:
                pygame.draw.rect(surface, (0, 0, 0), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), 2, border_radius=4)

        if self.breaking:
            selected_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player_pos, self.parent.size, TILE_SIZE)
            if selected_tile != self.real_tile:
                self.breaking = False
                self.breaking_percent = 0

            pygame.draw.rect(surface, (255, 0, 0), (self.breaking_tile[0] * TILE_SIZE, self.breaking_tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
            pygame.draw.rect(surface, (255, 0, 0), (self.breaking_tile[0] * TILE_SIZE, self.breaking_tile[1] * TILE_SIZE, TILE_SIZE * self.breaking_percent / 100, TILE_SIZE ))
            
            tile = Tiles.getTile(self.parent.save.getTile(self.real_tile[0], self.real_tile[1]))

            self.breaking_percent += Tiles.calculateHitPercent(self._breaking_power, tile.breaking_power, tile.durability)

            if self.breaking_percent >= 100:
                self.breaking = False
                self.breaking_percent = 0

                self.parent.save.setTile(self.real_tile[0], self.real_tile[1], TileIDS.GRASS)
                self.addToInventory(Item(tile.id, 1, pygame.image.load(tile.texture)))
                self.breaking_tile = None
            
    def onEvent(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            for i in range(len(self._keybind_map)):
                if Bindings.check(event, self._keybind_map[i]):
                    self._selected_slot = i
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.real_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player_pos, self.parent.size, TILE_SIZE)
                tile = Tiles.getTile(self.parent.save.getTile(self.real_tile[0], self.real_tile[1]))
                if tile.breakable:
                    self.breaking = True
                    self.breaking_percent = 0
                    self.breaking_tile = (event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE)
            # place block
            elif event.button == 3:
                selected_tile = Util.getTileLocation(pygame.mouse.get_pos(), self.parent.player_pos, self.parent.size, TILE_SIZE)
                if self._items[self._selected_slot] and self.parent.save.getTile(selected_tile[0], selected_tile[1]) == TileIDS.GRASS:
                    self.parent.save.setTile(selected_tile[0], selected_tile[1], self._items[self._selected_slot].item_id)
                    self._items[self._selected_slot].count -= 1
                    if self._items[self._selected_slot].count <= 0:
                        self._items[self._selected_slot] = None
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.breaking:
                    self.breaking = False
                    self.breaking_percent = 0