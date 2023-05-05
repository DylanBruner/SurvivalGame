import pygame, json
from game.keybinding import Bindings
from game.world import TileIDS, TEXTURE_MAPPINGS
from utils import Util
import game.particlesystem as pSys
from _types.item import Item

SLOT_TEXTURE: pygame.Surface = None

FONT = pygame.font.SysFont("Arial", 16)

class Config:
    # Visual
    SLOT_SIZE: int = 42
    ITEM_SIZE: int = 42 - 8 # 4px padding on each side
    BREAK_COLOR: pSys.Color = pSys.Color((70, 66, 38), mod_r=40)

    # Gameplay
    STACK_SIZE: int = 250

class Slot:
    def __init__(self, pos: tuple[int, int], item: Item = None, 
                 sLoc: tuple[int, int] = None, CAN_STORE: bool = True, 
                 HIDDEN: bool = False, COLLIDER_ONLY: bool = False):
        
        self.item: Item           = item
        self.saveLocation: tuple[int, int] = None
        self.pos: tuple[int, int] = pos
        self.sLoc: tuple[int, int] = sLoc
        self.CAN_STORE: bool       = CAN_STORE
        self.COLLIDER_ONLY: bool   = COLLIDER_ONLY
        self.HIDDEN: bool          = HIDDEN
        self.customOnClick         = lambda: None
        self._rect = pygame.Rect(pos, (Config.SLOT_SIZE, Config.SLOT_SIZE))

    def hasItem(self) -> bool:
        return self.item != None and self.item.item_id != 0 and self.item.count > 0

    def draw(self, surf: pygame.Surface) -> None:
        if self.HIDDEN and not self.hasItem(): return
        if self.COLLIDER_ONLY: return # just for visual code purposes

        # draw the slot texture
        surf.blit(SLOT_TEXTURE, self.pos)
        
        if self.item and (self.item.item_id != 0):
            surf.blit(self.item.texture, (self.pos[0] + 6, self.pos[1] + 6))
            q = FONT.render(str(self.item.count), True, (255, 255, 255))
            surf.blit(q, (self.pos[0] + 5, self.pos[1] + 5))
    
class PlayerStorage:
    def __init__(self, parent: object):
        self.parent = parent
        self.open   = False

        self.currentRecipe: dict = None
        self.openChestLocation: tuple[int, int] = None
        self.inventory: list[Slot]     = []
        self.craftingSlots: list[Slot] = []
        self.storageSlots: list[Slot]  = []
        self.hotbarSlots: list[Slot]   = []

        self._FIRST_CALL = True

    @Util.MonkeyUtils.autoErrorHandling
    def setup(self) -> None:
        global SLOT_TEXTURE

        self.width, self.height = 600, 400
        self.top_left = (self.parent.environment["current_size"][0] // 2 - self.width // 2, 
                         self.parent.environment["current_size"][1] // 2 - (self.height  * 1.2) // 2)

        # (350, 320), (390, 370)
        sheet = pygame.image.load("data/assets/ui_big_pieces.png")
        self.slot = pygame.Surface((40, 40))
        self.slot.blit(sheet, (0, 0), (353, 329, 40, 40))
        SLOT_TEXTURE = self.slot

        self.inventory: list[Slot]     = []
        self.craftingSlots: list[Slot] = []
        self.storageSlots: list[Slot]  = []
        self.hotbarSlots: list[Slot]   = []
        self.outputSlot: Slot          = Slot((265, 152), CAN_STORE=False) #TODO: Position
        self.outputSlot.customOnClick = self.itemCrafted

        xMod, yMod = 7, 225

        for y, row in enumerate(self.parent.save.save_data['player']['storage']):
            for x, item in enumerate(row):
                _x, _y = (self.top_left[0] + xMod) + x * Config.SLOT_SIZE, (self.top_left[1] + yMod) + y * Config.SLOT_SIZE
                self.inventory.append(Slot(
                    (_x, _y),
                    Item(item[0], item[1], TEXTURE_MAPPINGS[item[0]]),
                    sLoc=(x, y),
                ))
                self.inventory[-1].customOnClick = self.onInventoryModification
        
        # Storage slots
        # 8x4
        xMod, yMod = 259, 50
        for y in range(4):
            for x in range(8):
                _x, _y = (self.top_left[0] + xMod) + x * Config.SLOT_SIZE, (self.top_left[1] + yMod) + y * Config.SLOT_SIZE
                self.storageSlots.append(Slot((_x, _y), Item(0, 0, TEXTURE_MAPPINGS[1]), CAN_STORE=False, HIDDEN=True))

        # Hotbar slots
        self.hotbarSlots = []
        for rect in self.parent.hotbar.slotRects:
            item: Item = self.parent.hotbar._items[self.parent.hotbar.slotRects.index(rect)]
            rect: pygame.Rect
            self.hotbarSlots.append(Slot((rect.x, rect.y), item, COLLIDER_ONLY=True))
            self.hotbarSlots[-1].customOnClick = self.onHotbarModification
        
        # TEMP give the player some grass
        # self.inventory[5].item = Item(TileIDS.GRASS, 15, TEXTURE_MAPPINGS[1])
        
        # Crafting slots
        xMod, yMod = 7, 50
        for y in range(3):
            for x in range(3):
                _x, _y = (self.top_left[0] + xMod) + x * Config.SLOT_SIZE, (self.top_left[1] + yMod) + y * Config.SLOT_SIZE
                self.craftingSlots.append(Slot((_x, _y), Item(0, 0, TEXTURE_MAPPINGS[1])))

        self.dragItem: Item = None
        self.openChest: tuple[int, int] = None #TODO: change this to a container class maybe

        self.QUANTITY_FONT = pygame.font.SysFont("Arial", 16)
    
    @Util.MonkeyUtils.autoErrorHandling
    def onHotbarModification(self) -> None:
        for slot in self.hotbarSlots:
            self.parent.hotbar._items[self.hotbarSlots.index(slot)] = slot.item
        self.parent.hotbar.save()
    
    @Util.MonkeyUtils.autoErrorHandling
    def onInventoryModification(self) -> None:
        for slot in self.inventory:
            if slot.hasItem():
                self.parent.save.save_data['player']['storage'][slot.sLoc[1]][slot.sLoc[0]] = [slot.item.item_id, slot.item.count]
            else:
                self.parent.save.save_data['player']['storage'][slot.sLoc[1]][slot.sLoc[0]] = [0, 0]
        
    @Util.MonkeyUtils.autoErrorHandling
    def clearOpenChest(self) -> None:
        self.openChest = None
        for slot in self.storageSlots:
            slot.CAN_STORE = False
            slot.item = None
            slot.HIDDEN = True

    @Util.MonkeyUtils.autoErrorHandling
    def loadChestContents(self, location: tuple[int, int]) -> None:
        # print(self.parent.save.save_data['chests'][f"{location[1]},{location[0]}"])
        self.open = True
        self.parent.player.freeze = True
        self.openChest = location
        items: list[Item] = []
        for item in self.parent.save.save_data['chests'][f"{location[1]},{location[0]}"]:
            items.append(Item(item[0], item[1], TEXTURE_MAPPINGS[item[0]]))
        
        for slot in self.storageSlots:
            slot.CAN_STORE = True
            slot.item = None
            slot.HIDDEN = False
        
        for slot, item in zip(self.storageSlots, items):
            slot.item = item
            slot.customOnClick = self.saveChest
    
    @Util.MonkeyUtils.autoErrorHandling
    def saveChest(self):
        data = [(slot.item.item_id, slot.item.count) for slot in self.storageSlots if slot.item != None]
        self.parent.save.save_data['chests'][f"{self.openChest[1]},{self.openChest[0]}"] = data
        # print(self.parent.save.save_data['chests'][f"{self.openChest[1]},{self.openChest[0]}"])
        

    @Util.MonkeyUtils.autoErrorHandling
    def itemCrafted(self) -> None:
        if self.currentRecipe is not None:
            for y in range(3):
                for x in range(3):
                    if self.craftingSlots[y * 3 + x].item is not None:
                        self.craftingSlots[y * 3 + x].item.count -= self.currentRecipe['recipe'][y][x][1]
                        if self.craftingSlots[y * 3 + x].item.count <= 0:
                            self.craftingSlots[y * 3 + x].item = None
    
    @Util.MonkeyUtils.autoErrorHandling
    def updateCrafting(self) -> None:
        with open('data/config/recipes.json', 'r') as f:
            recipes = json.load(f)
        for recipe in recipes:
            matches = True

            for y in range(3):
                for x in range(3):
                    # make sure the crafting slot isn't none
                    if self.craftingSlots[y * 3 + x].item is not None:
                        if self.craftingSlots[y * 3 + x].item.item_id != recipe['recipe'][y][x][0] or self.craftingSlots[y * 3 + x].item.count < recipe['recipe'][y][x][1]:
                            matches = False
                    elif recipe['recipe'][y][x][0] != 0:
                        matches = False
            
            if matches:
                self.outputSlot.item = Item(recipe['result']['id'], recipe['result']['count'], TEXTURE_MAPPINGS[recipe['result']['id']])
                self.currentRecipe = recipe
                return
            else:
                self.outputSlot.item = None
                self.currentRecipe = None
    
    @Util.MonkeyUtils.autoErrorHandling
    def onOpen(self) -> None:
        # Code that needs to be ran every time the inventory is opened
        self.hotbarSlots = []
        for rect in self.parent.hotbar.slotRects:
            item: Item = self.parent.hotbar._items[self.parent.hotbar.slotRects.index(rect)]
            rect: pygame.Rect
            self.hotbarSlots.append(Slot((rect.x, rect.y), item, COLLIDER_ONLY=True))
            self.hotbarSlots[-1].customOnClick = self.onHotbarModification
        

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surf: pygame.Surface, env: dict) -> None:
        if self._FIRST_CALL: 
            self.setup()
            self._FIRST_CALL = False

        # 400 tall and 450 wide white rect that's centered
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(self.top_left, (self.width, self.height)), border_radius=12)

        for slot in self.inventory + self.craftingSlots + self.storageSlots + [self.outputSlot]:
            slot.draw(surf)
        
        if self.dragItem:
            surf.blit(self.dragItem.texture, pygame.mouse.get_pos())

    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event) -> None:
        if event.type == pygame.VIDEORESIZE:
            self.setup()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for slot in self.inventory + self.craftingSlots + [self.outputSlot] + self.storageSlots + self.hotbarSlots:
                if slot._rect.collidepoint(pygame.mouse.get_pos()):
                    if event.button == 1: # left click
                        if self.dragItem == None and slot.hasItem():
                            self.dragItem = slot.item
                            slot.item = None
                            slot.customOnClick()
                        
                        elif self.dragItem != None and not slot.hasItem() and slot.CAN_STORE:
                            slot.item = self.dragItem
                            self.dragItem = None
                            slot.customOnClick()
                        
                        elif self.dragItem != None and slot.hasItem() and slot.CAN_STORE:
                            if self.dragItem.item_id == slot.item.item_id:
                                slot.item.count += self.dragItem.count
                                self.dragItem = None
                                slot.customOnClick()
                    
                    elif event.button == 3: # right click
                        if self.dragItem != None and slot.CAN_STORE:
                            # place one item
                            if slot.hasItem() and slot.item.item_id == self.dragItem.item_id:
                                slot.item.count += 1
                                self.dragItem.count -= 1
                                slot.customOnClick()
                            elif not slot.hasItem():
                                slot.item = Item(self.dragItem.item_id, 1, self.dragItem.texture)
                                self.dragItem.count -= 1
                                slot.customOnClick()
                            
                            if self.dragItem.count <= 0:
                                self.dragItem = None
                                slot.customOnClick()
            self.updateCrafting()