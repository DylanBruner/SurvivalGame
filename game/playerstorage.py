import pygame, json
from game.keybinding import Bindings
from game.world import TileIDS, TEXTURE_MAPPINGS
from utils import Util
import game.particlesystem as pSys

SLOT_TEXTURE: pygame.Surface = None

class Config:
    # Visual
    SLOT_SIZE: int = 42
    ITEM_SIZE: int = 42 - 8 # 4px padding on each side
    BREAK_COLOR: pSys.Color = pSys.Color((70, 66, 38), mod_r=40)

    # Gameplay
    STACK_SIZE: int = 250

class Item:
    def __init__(self, item_id: int, count: int, texture: pygame.Surface):
        self.item_id = item_id
        self.count   = count
        self.texture = pygame.transform.scale(texture, (Config.ITEM_SIZE, Config.ITEM_SIZE)) # just in case

class Slot:
    def __init__(self, pos: tuple[int, int], item: Item = None):
        self.item: Item           = item
        self.pos: tuple[int, int] = pos

    def draw(self, surf: pygame.Surface) -> None:
        # draw the slot texture
        surf.blit(SLOT_TEXTURE, self.pos)
        
        # if self.item:
            # surf.blit(self.item.texture, self.pos)

class PlayerStorage:
    def __init__(self, parent: object):
        global SLOT_TEXTURE

        self.parent = parent
        self.open   = False

        # (350, 320), (390, 370)
        sheet = pygame.image.load("data/assets/ui_big_pieces.png")
        self.slot = pygame.Surface((40, 40))
        self.slot.blit(sheet, (0, 0), (353, 329, 40, 40))
        SLOT_TEXTURE = self.slot

        self.inventory: list[Slot]     = []
        self.craftingSlots: list[Slot] = []
        self.outputSlot: Slot          = Slot((0, 0)) #TODO: Position

        baseX = 107
        baseY = 280
    
        for y, row in enumerate(self.parent.save.save_data['player']['storage']):
            for x, item in enumerate(row):
                _x, _y = baseX + x * Config.SLOT_SIZE, baseY + y * Config.SLOT_SIZE
                self.inventory.append(Slot(
                    (_x, _y),
                    Item(item[0], item[1], TEXTURE_MAPPINGS[item[0]])
                ))

        self.dragging: bool = False
        self.dragItem: int  = (0, 0)

        self.openChest: tuple[int, int] = None

        self.QUANTITY_FONT = pygame.font.SysFont("Arial", 16)

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surf: pygame.Surface, env: dict) -> None:
        # 400 tall and 450 wide white rect that's centered
        width, height = 600, 400
        top_left      = (env["current_size"][0] // 2 - width // 2, env["current_size"][1] // 2 - (height  * 1.2) // 2)
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(top_left, (width, height)), border_radius=12)

        for slot in self.inventory:
            slot.draw(surf)
        
        for slot in self.craftingSlots:
            slot.draw(surf)
        
        self.outputSlot.draw(surf)

    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event) -> None:
        ...