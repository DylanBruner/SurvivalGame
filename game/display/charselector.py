import json

import pygame

from components.componentsystem import Component
from game.player.player import CHARACTERS
from util.myenvironment import Environment
from util.utils import Util

#94, 128 (192x192)
# 128, 128

class CharacterSelector(Component):
    """
    Character selector menu that allows the player to select their character.
    """
    def __init__(self, location: tuple[int, int]):
        super().__init__(location, (0, 0)) # size = tbd
        self.EVENT_SYSTEM_HOOKED = True # tell the game to send us events

        with open('data/config/settings.json', 'r') as f:
            self.selected_character: int = json.load(f)['player']['selected_character']
        
        UI_SPRITESHEET = pygame.image.load("data/assets/UI_elements.png")

        self.RIGHT_ARROW = UI_SPRITESHEET.subsurface(pygame.Rect(96, 128, 32, 32))
        self.RIGHT_ARROW = pygame.transform.rotate(self.RIGHT_ARROW, 180)
        self.LEFT_ARROW  = pygame.transform.rotate(self.RIGHT_ARROW.copy(), 180)

        # scale the left and right arrows to 2x their size
        self.RIGHT_ARROW = pygame.transform.scale(self.RIGHT_ARROW, (self.RIGHT_ARROW.get_width() * 2.2, self.RIGHT_ARROW.get_height() * 2.2))
        self.LEFT_ARROW  = pygame.transform.scale(self.LEFT_ARROW, (self.LEFT_ARROW.get_width() * 2.2, self.LEFT_ARROW.get_height() * 2.2))

        self.RIGHT_ARROW = pygame.transform.flip(self.RIGHT_ARROW, False, True)

        self.currentCharacter: pygame.Surface = self.getCharacterDisplay(self.selected_character)
    
    @Util.MonkeyUtils.autoErrorHandling
    def setSelectedCharacter(self, character: int):
        self.selected_character = character
        with open('data/config/settings.json', 'r') as f:
            settings = json.load(f)
            settings['player']['selected_character'] = character
        with open('data/config/settings.json', 'w') as f:
            json.dump(settings, f)

    @Util.MonkeyUtils.autoErrorHandling
    def getCharacterDisplay(self, character: int) -> pygame.Surface:
        path = "data/assets/character/characters_pack_extended/Heroes/" + CHARACTERS[character]
        img = pygame.image.load(path).subsurface(pygame.Rect(0, 64, 24, 32))
        img = pygame.transform.scale(img, (img.get_width() * 8, img.get_height() * 8))
        img.set_colorkey((0, 117, 117))
        return img
    
    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, environment: Environment):
        surface.blit(self.LEFT_ARROW, (self.location[0] - self.LEFT_ARROW.get_width(), self.location[1] + (self.currentCharacter.get_height() // 1.24) - self.LEFT_ARROW.get_height()))
        surface.blit(self.currentCharacter, self.location)
        surface.blit(self.RIGHT_ARROW, (self.location[0] + self.currentCharacter.get_width(), self.location[1] + (self.currentCharacter.get_height() // 1.24) - self.RIGHT_ARROW.get_height()))

    @Util.MonkeyUtils.autoErrorHandling
    def onEvent(self, event: pygame.event.Event):
        """
        If the player clicks on the left or right arrow, change the selected character.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.LEFT_ARROW.get_rect(topleft = (self.location[0] - self.LEFT_ARROW.get_width(), self.location[1] + (self.currentCharacter.get_height() // 1.4) - self.LEFT_ARROW.get_height())).collidepoint(event.pos):
                    self.selected_character -= 1
                    if self.selected_character < 0:
                        self.selected_character = len(CHARACTERS) - 2
                    self.currentCharacter = self.getCharacterDisplay(self.selected_character)
                    self.setSelectedCharacter(self.selected_character)
                elif self.RIGHT_ARROW.get_rect(topleft = (self.location[0] + self.currentCharacter.get_width(), self.location[1] + (self.currentCharacter.get_height() // 1.4) - self.RIGHT_ARROW.get_height())).collidepoint(event.pos):
                    self.selected_character += 1
                    if self.selected_character > len(CHARACTERS) - 2:
                        self.selected_character = 0
                    self.currentCharacter = self.getCharacterDisplay(self.selected_character)
                    self.setSelectedCharacter(self.selected_character)