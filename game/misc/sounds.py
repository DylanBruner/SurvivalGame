import pygame
from util.utils import Util

pygame.mixer.init()

class Sounds:
    """
    Nothing to really comment here everything is kinda obvious
    """
    MENU_CLICK  = pygame.mixer.Sound("data/assets/sounds/menu_click.wav")
    BLOCK_BREAK = pygame.mixer.Sound("data/assets/sounds/block_break.wav")

    @staticmethod
    @Util.MonkeyUtils.autoErrorHandling
    def playSound(sound: pygame.mixer.Sound):
        sound.play()