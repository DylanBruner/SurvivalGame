import pygame
from myenvironment import Environment
from utils import Util

class Enemy:
    def __init__(self, location: tuple[int, int], health: int = 100):
        self.location = location
        self.health   = health
        self.alive    = True

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, environment: Environment, location: tuple[int, int]):
        pygame.draw.circle(surface, (0, 0, 255), location, 10)