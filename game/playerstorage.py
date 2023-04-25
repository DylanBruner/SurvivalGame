import pygame
from game.keybinding import Bindings
from game.world import TileIDS, TEXTURE_MAPPINGS

class PlayerStorage:
    def __init__(self, parent: object):
        self.parent = parent
        self.open   = False

        # (350, 320), (390, 370)
        sheet = pygame.image.load("data/assets/ui_big_pieces.png")
        self.slot = pygame.Surface((40, 40))
        self.slot.blit(sheet, (0, 0), (353, 329, 40, 40))

        # 9x4 2d list filled of 0's
        self.inventory     = [[(0, 0) for _ in range(14)] for _ in range(4)] # ID, Quantity
        self.slotLocations = [[None for _ in range(14)] for _ in range(4)]

        self.inventory[0][5] = (1, 9)

        self.dragging: bool              = True
        self.dragOrigin: tuple[int, int] = None
        self.dragItem: int               = (1, 5)

        self.QUANTITY_FONT = pygame.font.SysFont("Arial", 16)

    def draw(self, surf: pygame.Surface, env: dict) -> None:
        # 400 tall and 450 wide white rect that's centered
        width, height = 600, 400
        top_left      = (env["current_size"][0] // 2 - width // 2, env["current_size"][1] // 2 - (height  * 1.2) // 2)
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(top_left, (width, height)))

        # draw the slots
        startY = top_left[1] + 140
        for y in range(len(self.inventory)):
            for x in range(len(self.inventory[y])):
                surf.blit(self.slot, (top_left[0] + 20 + (x * 40), startY + top_left[1] + 20 + (y * 40)))
                self.slotLocations[y][x] = (top_left[0] + 20 + (x * 40), startY + top_left[1] + 20 + (y * 40))

                # draw the item centered in the slot
                if self.inventory[y][x] != (0, 0):
                    surf.blit(pygame.transform.scale(TEXTURE_MAPPINGS[self.inventory[y][x][0]], (32, 32)), (top_left[0] + 20 + (x * 40) + 4, startY + top_left[1] + 20 + (y * 40) + 4))
                    # draw the quantity in the top left
                    if self.inventory[y][x][1] > 1:
                        text = self.QUANTITY_FONT.render(str(self.inventory[y][x][1]), True, (255, 255, 255))
                        surf.blit(text, (top_left[0] + 26 + (x * 40), startY + top_left[1] + 26 + (y * 40)))
        

        if self.dragging:
            surf.blit(TEXTURE_MAPPINGS[self.dragItem[0]], pygame.mouse.get_pos())

    def getSlotLocation(self, pos: tuple[int, int]) -> tuple[int, int]:
        for y in range(len(self.slotLocations)):
            for x in range(len(self.slotLocations[y])):
                if self.slotLocations[y][x][0] < pos[0] < self.slotLocations[y][x][0] + self.slot.get_width() and self.slotLocations[y][x][1] < pos[1] < self.slotLocations[y][x][1] + self.slot.get_height():
                    return x, y
        return (-1, -1)

    def onEvent(self, event: pygame.event.Event) -> None:
        # if it's mousedown and the mouse is in the inventory get the selected slot
        if event.type == pygame.MOUSEBUTTONDOWN and self.open:
            # calculate the slotX and slotY location
            slotX, slotY = self.getSlotLocation(event.pos)
            if slotX == -1 and slotY == -1: return

            # if the slot is empty and the player is holding an item
            if self.inventory[slotY][slotX] == (0, 0) and self.dragging:
                self.inventory[slotY][slotX] = self.dragItem
                self.dragging = False

            # if the slot is not empty and the player is holding an item
            elif self.inventory[slotY][slotX] != (0, 0) and self.dragging:
                # see if we can stack the items (up to 250)
                if self.inventory[slotY][slotX][0] == self.dragItem[0] and self.inventory[slotY][slotX][1] < 250:
                    self.inventory[slotY][slotX] = (self.dragItem[0], self.inventory[slotY][slotX][1] + self.dragItem[1])
                    self.dragging = False

                # if the quantity is over 250 then just swap the items
                elif self.inventory[slotY][slotX][0] == self.dragItem[0] and self.inventory[slotY][slotX][1] >= 250:
                    self.inventory[slotY][slotX], self.dragItem = self.dragItem, self.inventory[slotY][slotX]
            
            # elif not dragging and shift is pressed and the slot isnt empty
            elif not self.dragging and pygame.key.get_pressed()[pygame.K_LSHIFT] and self.inventory[slotY][slotX] != (0, 0):
                print("moving to hotbar")
                
            elif not self.dragging and self.inventory[slotY][slotX] != (0, 0):
                self.dragging = True
                self.dragItem = self.inventory[slotY][slotX]
                self.inventory[slotY][slotX] = (0, 0)
            