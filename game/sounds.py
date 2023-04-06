import pygame

pygame.mixer.init()

class Sounds:
    MENU_CLICK  = pygame.mixer.Sound("data/assets/sounds/menu_click.wav")
    BLOCK_BREAK = pygame.mixer.Sound("data/assets/sounds/block_break.wav")

    @staticmethod
    def playSound(sound: pygame.mixer.Sound):
        sound.play()