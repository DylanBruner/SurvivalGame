import pygame, math
from myenvironment import Environment
from game.enemy import Enemy
from utils import Util
from game.world import TILE_SIZE

class TestPathfinderEnemy(Enemy):
    def __init__(self, location: tuple[int, int], parent):
        super().__init__(location, 100)
        self.parent = parent # reference to the gameview viewport

        self.speed  = 0.09
        self.facing = 0
        self.FOV    = 90
        self.VIEW_DISTANCE = 100

        self.player_location = None

    @Util.MonkeyUtils.autoErrorHandling
    def canSeePlayer(self) -> bool:
        player_location = self.parent.player.location
        for i in range(self.VIEW_DISTANCE):
            # check if the player is in the FOV
            if Util.distance((self.location[0] + math.cos(self.facing) * i, self.location[1] + math.sin(self.facing) * i), player_location) < 1:
                return True
        return False

    @Util.MonkeyUtils.autoErrorHandling
    def findingPlayer(self, environment: Environment):
        self.facing += 0.01
        if self.canSeePlayer():
            self.player_location = self.parent.player.location
    
    @Util.MonkeyUtils.autoErrorHandling
    def moveTowardsPlayer(self, environment: Environment):
        if self.player_location:
            if Util.distance(self.location, self.player_location) < 1:
                self.player_location = None
                return
            self.facing = math.atan2(self.player_location[1] - self.location[1], self.player_location[0] - self.location[0])
            self.location = (self.location[0] + math.cos(self.facing) * self.speed, self.location[1] + math.sin(self.facing) * self.speed)

    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, environment: Environment, location: tuple[int, int]):
        super().draw(surface, environment, location)

        if not self.player_location:
            self.findingPlayer(environment)
        else:
            if self.canSeePlayer():
                self.player_location = self.parent.player.location
            self.moveTowardsPlayer(environment)
        
        # draw the FOV
        pygame.draw.line(surface, (255, 0, 0), location, (location[0] + math.cos(self.facing) * 100, location[1] + math.sin(self.facing) * 100), 2)
        pygame.draw.line(surface, (255, 0, 0), location, (location[0] + math.cos(self.facing + math.radians(self.FOV / 2)) * 100, location[1] + math.sin(self.facing + math.radians(self.FOV / 2)) * 100), 2)
        pygame.draw.line(surface, (255, 0, 0), location, (location[0] + math.cos(self.facing - math.radians(self.FOV / 2)) * 100, location[1] + math.sin(self.facing - math.radians(self.FOV / 2)) * 100), 2)