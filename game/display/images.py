import pygame

pygame.init()
# set a video mode

class Images:
    def __init__(self):
        UI_SPRITESHEET = pygame.image.load("data/assets/UI_elements.png").convert_alpha()
        self.BUTTON_IDLE: pygame.Surface  = UI_SPRITESHEET.subsurface(pygame.Rect(96, 0, 96, 32))
        self.BUTTON_HOVER: pygame.Surface = UI_SPRITESHEET.subsurface(pygame.Rect(96, 32, 96, 32))
        self.BUTTON_CLICK: pygame.Surface = UI_SPRITESHEET.subsurface(pygame.Rect(96, 64, 96, 32))

        self.BUTTON_IDLE = pygame.transform.scale(self.BUTTON_IDLE, (self.BUTTON_IDLE.get_width() * 2, self.BUTTON_IDLE.get_height() * 2))
        self.BUTTON_HOVER = pygame.transform.scale(self.BUTTON_HOVER, (self.BUTTON_HOVER.get_width() * 2, self.BUTTON_HOVER.get_height() * 2))
        self.BUTTON_CLICK = pygame.transform.scale(self.BUTTON_CLICK, (self.BUTTON_CLICK.get_width() * 2, self.BUTTON_CLICK.get_height() * 2))