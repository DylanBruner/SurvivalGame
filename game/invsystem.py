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

    def draw(self, surface: pygame.Surface, enviorment: dict):
        for i in range(len(self._items)):
            pygame.draw.rect(surface, (255, 255, 255), (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING), self.location[1], Config.SLOT_SIZE, Config.SLOT_SIZE), border_radius=(4 if i == self._selected_slot else 0))
            # draw item
            if self._items[i]:
                surface.blit(self._items[i].texture, (self.location[0] + i * (Config.SLOT_SIZE + self.SLOT_SPACING) + 4, self.location[1] + 4))
            
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
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.breaking:
                    self.breaking = False
                    self.breaking_percent = 0