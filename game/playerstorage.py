import pygame, json
from game.keybinding import Bindings
from game.world import TileIDS, TEXTURE_MAPPINGS
from utils import Util
import game.particlesystem as pSys

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


class PlayerStorage:
    def __init__(self, parent: object):
        self.parent = parent
        self.open   = False

        # (350, 320), (390, 370)
        sheet = pygame.image.load("data/assets/ui_big_pieces.png")
        self.slot = pygame.Surface((40, 40))
        self.slot.blit(sheet, (0, 0), (353, 329, 40, 40))

        # 9x4 2d list filled of 0's
        self.inventory     = self.parent.save.save_data['player']['storage']
        self.slotLocations = [[None for _ in range(14)] for _ in range(4)]

        self.craftingSlots = [[None for _ in range(3)] for _ in range(3)]
        self.outputSlot    = (0, 0)
        self.currentRecipe = None

        self.dragging: bool              = False
        self.dragOrigin: tuple[int, int] = None
        self.dragItem: int               = (0, 0)

        self.QUANTITY_FONT = pygame.font.SysFont("Arial", 16)

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surf: pygame.Surface, env: dict) -> None:
        # 400 tall and 450 wide white rect that's centered
        width, height = 600, 400
        top_left      = (env["current_size"][0] // 2 - width // 2, env["current_size"][1] // 2 - (height  * 1.2) // 2)
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(top_left, (width, height)), border_radius=12)

        # draw the slots
        startY = top_left[1] + 140
        for y in range(len(self.inventory)):
            for x in range(len(self.inventory[y])):
                surf.blit(self.slot, (top_left[0] + 20 + (x * 40), startY + top_left[1] + 20 + (y * 40)))
                self.slotLocations[y][x] = (top_left[0] + 20 + (x * 40), startY + top_left[1] + 20 + (y * 40))

                # draw the item centered in the slot
                if self.inventory[y][x][0] != 0:
                    surf.blit(pygame.transform.scale(TEXTURE_MAPPINGS[self.inventory[y][x][0]], (32, 32)), (top_left[0] + 20 + (x * 40) + 4, startY + top_left[1] + 20 + (y * 40) + 4))
                    # draw the quantity in the top left
                    if self.inventory[y][x][1] > 1:
                        text = self.QUANTITY_FONT.render(str(self.inventory[y][x][1]), True, (255, 255, 255))
                        surf.blit(text, (top_left[0] + 26 + (x * 40), startY + top_left[1] + 26 + (y * 40)))
        
        # draw the crafting slots
        topLeft = (100, 60)
        for y in range(len(self.craftingSlots)):
            for x in range(len(self.craftingSlots[y])):
                surf.blit(self.slot, (topLeft[0] + 20 + (x * 40), topLeft[1] + 20 + (y * 40)))
                if self.craftingSlots[y][x] is not None:
                    surf.blit(pygame.transform.scale(TEXTURE_MAPPINGS[self.craftingSlots[y][x][0]], (32, 32)), (topLeft[0] + 20 + (x * 40) + 4, topLeft[1] + 20 + (y * 40) + 4)) 
                    # draw the quantity in the top left
                    if self.craftingSlots[y][x][1] > 1:
                        text = self.QUANTITY_FONT.render(str(self.craftingSlots[y][x][1]), True, (255, 255, 255))
                        surf.blit(text, (topLeft[0] + 26 + (x * 40), topLeft[1] + 26 + (y * 40)))

        # draw the output slot
        slotLocation = (270, 120)
        surf.blit(self.slot, slotLocation)

        if self.outputSlot is not None and self.outputSlot != (0, 0):
            surf.blit(pygame.transform.scale(TEXTURE_MAPPINGS[self.outputSlot[0]], (32, 32)), (slotLocation[0] + 4, slotLocation[1] + 4)) 

        
        if self.dragging:
            surf.blit(TEXTURE_MAPPINGS[self.dragItem[0]], pygame.mouse.get_pos())
            # draw the quantity in the top left
            if self.dragItem[1] > 1:
                text = self.QUANTITY_FONT.render(str(self.dragItem[1]), True, (255, 255, 255))
                surf.blit(text, pygame.mouse.get_pos())

    @Util.MonkeyUtils.autoErrorHandling
    def getSlotLocation(self, pos: tuple[int, int]) -> tuple[int, int]:
        for y in range(len(self.slotLocations)):
            for x in range(len(self.slotLocations[y])):
                if self.slotLocations[y][x][0] < pos[0] < self.slotLocations[y][x][0] + self.slot.get_width() and self.slotLocations[y][x][1] < pos[1] < self.slotLocations[y][x][1] + self.slot.get_height():
                    return x, y
        return (-1, -1)
    
    @Util.MonkeyUtils.autoErrorHandling
    def updateCrafting(self) -> None:
        with open('data/config/recipes.json', 'r') as f:
            recipes = json.load(f)

        for recipe in recipes:
            if not recipe["shapeless"]:
                for y in range(len(self.craftingSlots)):
                    for x in range(len(self.craftingSlots[y])):
                        if recipe["recipe"][y][x] != [0, 0] and self.craftingSlots[y][x] is not None:
                            if recipe["recipe"][y][x][0] > self.craftingSlots[y][x][0] or recipe["recipe"][y][x][1] > self.craftingSlots[y][x][1]: 
                                break
                        elif recipe["recipe"][y][x] != [0, 0] and self.craftingSlots[y][x] is None:
                            break
                        elif recipe["recipe"][y][x] == [0, 0] and self.craftingSlots[y][x] is not None:
                            break
                    else:
                        continue
                    break
                else:
                    self.outputSlot = (recipe["result"]["id"], recipe["result"]["count"])
                    self.currentRecipe = recipe
                    return
        
        self.outputSlot = None
    
    @Util.MonkeyUtils.autoErrorHandling
    def craft(self) -> None:
        # remove the amount of items from the crafting slots
        for y in range(len(self.craftingSlots)):
            for x in range(len(self.craftingSlots[y])):
                if self.craftingSlots[y][x] is not None:
                    self.craftingSlots[y][x] = (self.craftingSlots[y][x][0], self.craftingSlots[y][x][1] - self.currentRecipe["recipe"][y][x][1])
                    if self.craftingSlots[y][x][1] == 0:
                        self.craftingSlots[y][x] = None
        self.updateCrafting()


    @Util.MonkeyUtils.autoErrorHandling
    def addItem(self, item: Item):
        for y in range(len(self.inventory)):
            for x in range(len(self.inventory[y])):
                if self.inventory[y][x] == (0, 0):
                    self.inventory[y][x] = (item.item_id, item.count)
                    return
                
                elif self.inventory[y][x][0] == item.item_id and self.inventory[y][x][1] + item.count <= 250:
                    self.inventory[y][x] = (item.item_id, self.inventory[y][x][1] + item.count)
                    return

    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event) -> None:
        # if it's mousedown and the mouse is in the inventory get the selected slot
        if event.type == pygame.MOUSEBUTTONDOWN and self.open:
            # calculate the slotX and slotY location
            slotX, slotY = self.getSlotLocation(event.pos)
            if slotX == -1 and slotY == -1:
                # check if it's one of the crafting slots
                for y in range(len(self.craftingSlots)):
                    for x in range(len(self.craftingSlots[y])):
                        topLeft = (100, 60)
                        loc     = (topLeft[0] + 20 + (x * 40), topLeft[1] + 20 + (y * 40))
                        mouse   = pygame.mouse.get_pos()

                        transferMode = -1
                        if event.button == 1: # left click, whole stack
                            transferMode = 0
                        elif event.button == 3: # right click, 1 item
                            transferMode = 1
                        
                        if transferMode == -1: continue

                        # this code sucks but whatever
                        if loc[0] < mouse[0] < loc[0] + self.slot.get_width() and loc[1] < mouse[1] < loc[1] + self.slot.get_height():
                            # if we are holding an item and the slot is empty then put the item in the slot (1 item if right click, whole stack if left click)
                            if self.dragging and self.craftingSlots[y][x] is None:
                                if transferMode == 0:
                                    self.craftingSlots[y][x] = self.dragItem
                                    self.dragging = False
                                    self.updateCrafting()
                                elif transferMode == 1:
                                    self.craftingSlots[y][x] = (self.dragItem[0], 1)
                                    self.dragItem = (self.dragItem[0], self.dragItem[1] - 1)
                                    if self.dragItem[1] <= 0:
                                        self.dragging = False
                                    self.updateCrafting()
                                    break
                            
                            # if the slot is not empty and we are holding an item then try to stack the items, (1 item if right click, whole stack if left click)
                            elif self.dragging and self.craftingSlots[y][x] is not None:
                                if self.craftingSlots[y][x][0] == self.dragItem[0] and self.craftingSlots[y][x][1] < 250:
                                    if transferMode == 0:
                                        self.craftingSlots[y][x] = (self.dragItem[0], self.craftingSlots[y][x][1] + self.dragItem[1])
                                        self.dragging = False
                                        self.updateCrafting()
                                    elif transferMode == 1:
                                        self.craftingSlots[y][x] = (self.dragItem[0], self.craftingSlots[y][x][1] + 1)
                                        self.dragItem = (self.dragItem[0], self.dragItem[1] - 1)
                                        if self.dragItem[1] <= 0:
                                            self.dragging = False
                                        self.updateCrafting()
                                        break
                            
                            # if the slot is not empty and we are not holding an item then pick up the item (1 item if right click, whole stack if left click)
                            elif not self.dragging and self.craftingSlots[y][x] is not None:
                                if transferMode == 0:
                                    self.dragItem = self.craftingSlots[y][x]
                                    self.dragging = True
                                    self.updateCrafting()

                                    self.dragging = True
                                    self.dragItem = self.craftingSlots[y][x]
                                    self.craftingSlots[y][x] = None
                                elif transferMode == 1:
                                    self.dragItem = (self.craftingSlots[y][x][0], 1)
                                    self.craftingSlots[y][x] = (self.craftingSlots[y][x][0], self.craftingSlots[y][x][1] - 1)
                                    self.dragging = True
                                    self.dragItem = (self.craftingSlots[y][x][0], 1)
                                    
                                    if self.craftingSlots[y][x][1] <= 0:
                                        self.craftingSlots[y][x] = None
                                    self.updateCrafting()
                                    break

                            self.updateCrafting()
                            break
            
                # check if the output slot was clicked, 270, 100
                if 270 < event.pos[0] < 270 + self.slot.get_width() and 100 < event.pos[1] < 100 + self.slot.get_height() + 20:
                    if self.outputSlot is not None:
                        item = Item(self.outputSlot[0], self.outputSlot[1], TEXTURE_MAPPINGS[self.outputSlot[0]])
                        self.addItem(item)
                        self.craft()
                return

            # if the slot is empty and the player is holding an item
            if self.inventory[slotY][slotX][0] == 0 and self.dragging:
                self.inventory[slotY][slotX] = self.dragItem
                self.dragging = False

            # if the slot is not empty and the player is holding an item
            elif self.inventory[slotY][slotX][0] != 0 and self.dragging:
                # see if we can stack the items (up to 250)
                if self.inventory[slotY][slotX][0] == self.dragItem[0] and self.inventory[slotY][slotX][1] < 250:
                    self.inventory[slotY][slotX] = (self.dragItem[0], self.inventory[slotY][slotX][1] + self.dragItem[1])
                    self.dragging = False

                # if the quantity is over 250 then just swap the items
                elif self.inventory[slotY][slotX][0] == self.dragItem[0] and self.inventory[slotY][slotX][1] >= 250:
                    self.inventory[slotY][slotX], self.dragItem = self.dragItem, self.inventory[slotY][slotX]
            
            # elif not dragging and shift is pressed and the slot isnt empty
            elif not self.dragging and pygame.key.get_pressed()[pygame.K_LSHIFT] and self.inventory[slotY][slotX][0] != 0:
                hotbar = None  
                for component in self.parent.components['components']:
                    if component.__class__.__name__ == "HotbarComponent":
                        hotbar = component
                        break

                item = Item(self.inventory[slotY][slotX][0], self.inventory[slotY][slotX][1], TEXTURE_MAPPINGS[self.inventory[slotY][slotX][0]])
                hotbar.addToInventory(item)
                self.inventory[slotY][slotX] = (0, 0)

            elif not self.dragging and self.inventory[slotY][slotX][0] != 0:
                self.dragging = True
                self.dragItem = self.inventory[slotY][slotX]
                self.inventory[slotY][slotX] = (0, 0)
            
            keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
            if self.getSlotLocation(event.pos)[1] != -1 and any(pygame.key.get_pressed()[key] for key in keys):
                keyPressed = [key for key in keys if pygame.key.get_pressed()[key]][0]
                hotbar = None
                for component in self.parent.components['components']:
                    if component.__class__.__name__ == "HotbarComponent":
                        hotbar = component
                        break
                
                # if there is an item in the slot move it into the inventory
                if hotbar._items[keyPressed - 49] != (0, 0) and hotbar._items[keyPressed - 49] != [0, 0]:
                    item: Item = hotbar._items[keyPressed - 49]
                    if item is not None:
                        hotbar._items[keyPressed - 49] = None
                        hotbar.save()
                        self.addItem(item)