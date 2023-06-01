import pygame

from util.funccache import Cache

rarities = [
    (255, 255, 255),
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (255, 165, 0)
]

RARITY_COMMON   = 0
RARITY_UNCOMMON = 1
RARITY_RARE     = 2
RARITY_EPIC     = 3
RARITY_LEGENDARY= 4

pygame.init()
loreFont = pygame.font.SysFont("Arial", 14)

class Text:
    def __init__(self, text: str, 
                 BOLD: bool = False, ITALIC: bool = False, COLOR: tuple[int, int, int] = (255, 255, 255)):
        
        self.text: str       = text
        self.BOLD: bool      = BOLD
        self.ITALIC: bool    = ITALIC
        self.COLOR: tuple[int, int, int] = COLOR


class Lore:
    """
    Class for generating lore boxes for items
    """
    @staticmethod
    def _autoWordWrap(lines: list[Text]):
        # split any lines that need splitting for the width of the lore box
        newLines = []
        for line in lines:
            width = loreFont.size(line.text)[0]
            if width > 92:
                # split the line
                words = line.text.split(" ")
                newLine = ""
                for word in words:
                    if loreFont.size(newLine + word)[0] > 92:
                        newLines.append(Text(newLine, line.BOLD, line.ITALIC, line.COLOR))
                        newLine = ""
                    newLine += word + " "
                newLines.append(Text(newLine, line.BOLD, line.ITALIC, line.COLOR))
            else:
                newLines.append(line)
        return newLines
    
    @staticmethod
    @Cache.cache()
    def renderLore(itemName: str, itemRarity: int, lines: list[Text]) -> pygame.Surface:
        lines = Lore._autoWordWrap(lines)

        HEIGHT, WIDTH = 30, 100
        for line in lines:
            HEIGHT += 16

        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        # draw a border around the surface with rounded corners filled in with black and a white outline
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, WIDTH, HEIGHT), 2, border_radius=4)
        pygame.draw.rect(surface, (20, 20, 20), (2, 2, WIDTH-4, HEIGHT-4), border_radius=4)

        # item name in top left corner
        name = loreFont.render(itemName, True, rarities[itemRarity])
        surface.blit(name, (4, 4))

        # draw the lines of text
        loreStart = 20
        for line in lines:
            font = pygame.font.SysFont("Arial", 14, bold=line.BOLD, italic=line.ITALIC)
            text = font.render(line.text, True, line.COLOR)
            surface.blit(text, (4, loreStart))
            loreStart += 16

        return surface
    
# Storing the lore here is stupid, it should be within the item config file but whatever
BASE_ITEM_LORE = {
    "1": {"name": "Grass", "rarity": RARITY_COMMON, "lore": []},
    "2": {"name": "Water", "rarity": RARITY_COMMON, "lore": []},
    "3": {"name": "Stone", "rarity": RARITY_COMMON, "lore": []},
    "4": {"name": "Tree", "rarity": RARITY_COMMON, "lore": []},
    "5": {"name": "Tree", "rarity": RARITY_COMMON, "lore": []},
    "6": {"name": "Tree", "rarity": RARITY_COMMON, "lore": []},
    "7": {"name": "Tree", "rarity": RARITY_COMMON, "lore": []},
    "8": {"name": "Wood", "rarity": RARITY_COMMON, "lore": []},
    "9": {"name": "Chest", "rarity": RARITY_COMMON, "lore": []},
    "10": {"name": "Sand", "rarity": RARITY_COMMON, "lore": []},
    "11": {"name": "Torch", "rarity": RARITY_COMMON, "lore": []},
}