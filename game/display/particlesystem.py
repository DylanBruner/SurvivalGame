import math
import random
import time
import sys

import pygame

from util.utils import Util


class Shape:
    CIRCLE    = 0
    RECTANGLE = 1
    STAR      = 2
    TRIANGLE  = 3
    HEXAGON   = 4
    RANDOM    = 5
    RANDOM_POLYGON = 6

class Color:
    def __init__(self, base: tuple[int, int, int], mod_r: int = 0):
        self.base  = base
        self.mod_r = mod_r
    
    @Util.MonkeyUtils.autoErrorHandling
    def get(self) -> tuple[int, int, int]:
        c = (self.base[0] + random.randint(-self.mod_r, self.mod_r), 
                self.base[1] + random.randint(-self.mod_r, self.mod_r), 
                self.base[2] + random.randint(-self.mod_r, self.mod_r))
        return (max(0, min(255, c[0])), max(0, min(255, c[1])), max(0, min(255, c[2])))

class ParticleDisplay:
    """
    This code is awful i planned to rewrite it but i never got around to it seeing as it worked well enough
    """
    def __init__(self, start: tuple[int, int], color: Color, shape: int, 
                 count: int, speed: int, size: int = 2, lifetime: int = 700, lifetime_variance: int = 250):
        self.start = start
        self.shape = shape
        self.count = count
        self.color = color
        self.speed = speed
        self.size  = size
        self.lifetime = lifetime
        self.lifetime_variance = lifetime_variance

        self.particles = [(start[0] + random.randint(-10, 10), start[1] + random.randint(-10, 10)) for _ in range(count)]
        self.start_time = time.time()
    
    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, surface: pygame.Surface, delta_time: int = 1) -> None:
        self.mod_particles = self.particles.copy()
        for particle in self.particles:
            try:
                # convert the time to ms
                if time.time() - self.start_time > self.lifetime / 1000 + random.randint(-self.lifetime_variance, self.lifetime_variance) / 1000:
                    self.mod_particles.remove(particle)
                    continue
                else:
                    o_particle = particle
                    # spread the particles out from the center, also add prefrence to stay away from each other
                    closest = None
                    for other in self.particles:
                        if other == particle:
                            continue
                        if closest is None:
                            closest = other
                        elif math.sqrt((other[0] - particle[0]) ** 2 + (other[1] - particle[1]) ** 2) < math.sqrt((closest[0] - particle[0]) ** 2 + (closest[1] - particle[1]) ** 2):
                            closest = other
                    if closest is not None:
                        particle = (particle[0] + (closest[0] - particle[0]) / 10, particle[1] + (closest[1] - particle[1]) / 10)
                    particle = (particle[0] + random.randint(-self.speed, self.speed), particle[1] + random.randint(-self.speed, self.speed))
                    self.mod_particles[self.particles.index(o_particle)] = particle

                if self.shape == Shape.CIRCLE:
                    pygame.draw.circle(surface, self.color.get(), particle, self.size)
                elif self.shape == Shape.RECTANGLE:
                    pygame.draw.rect(surface, self.color.get(), (particle[0], particle[1], self.size, self.size))
                elif self.shape == Shape.STAR:
                    pygame.draw.polygon(surface, self.color.get(), ((particle[0], particle[1] - self.size), 
                                                                (particle[0] - self.size, particle[1] + self.size), 
                                                                (particle[0] + self.size, particle[1] + self.size)))
                elif self.shape == Shape.TRIANGLE:
                    pygame.draw.polygon(surface, self.color.get(), ((particle[0] - self.size, particle[1] - self.size), 
                                                                (particle[0] + self.size, particle[1] - self.size), 
                                                                (particle[0], particle[1] + self.size)))
                elif self.shape == Shape.HEXAGON:
                    pygame.draw.polygon(surface, self.color.get(), ((particle[0] - self.size, particle[1]), 
                                                                (particle[0] - self.size / 2, particle[1] - self.size), 
                                                                (particle[0] + self.size / 2, particle[1] - self.size), 
                                                                (particle[0] + self.size, particle[1]), 
                                                                (particle[0] + self.size / 2, particle[1] + self.size), 
                                                                (particle[0] - self.size / 2, particle[1] + self.size)))
                elif self.shape == Shape.RANDOM_POLYGON:
                    sides = random.randint(3, 10)
                    points = []
                    for i in range(sides):
                        points.append((particle[0] + self.size * math.cos(2 * math.pi * i / sides), 
                                    particle[1] + self.size * math.sin(2 * math.pi * i / sides)))
                    pygame.draw.polygon(surface, self.color.get(), points)
                    
                elif self.shape == Shape.RANDOM:
                    shape = random.randint(0, 4)
                    if shape == Shape.CIRCLE:
                        pygame.draw.circle(surface, self.color.get(), particle, self.size)
                    elif shape == Shape.RECTANGLE:
                        pygame.draw.rect(surface, self.color.get(), (particle[0], particle[1], self.size, self.size))
                    elif shape == Shape.STAR:
                        pygame.draw.polygon(surface, self.color.get(), ((particle[0], particle[1] - self.size), 
                                                                    (particle[0] - self.size, particle[1] + self.size), 
                                                                    (particle[0] + self.size, particle[1] + self.size)))
                    elif shape == Shape.TRIANGLE:
                        pygame.draw.polygon(surface, self.color.get(), ((particle[0] - self.size, particle[1] - self.size),
                                                                        (particle[0] + self.size, particle[1] - self.size),
                                                                        (particle[0], particle[1] + self.size)))
                    elif shape == Shape.HEXAGON:
                        pygame.draw.polygon(surface, self.color.get(), ((particle[0] - self.size, particle[1]), 
                                                                    (particle[0] - self.size / 2, particle[1] - self.size), 
                                                                    (particle[0] + self.size / 2, particle[1] - self.size), 
                                                                    (particle[0] + self.size, particle[1]), 
                                                                    (particle[0] + self.size / 2, particle[1] + self.size), 
                                                                    (particle[0] - self.size / 2, particle[1] + self.size)))
            except (IndexError, ValueError) as e:
                ...
        self.particles = self.mod_particles

# Code for testing the particle system, only runs if this file is run directly
if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    particleDisplays: list[ParticleDisplay] = []
    font = pygame.font.SysFont('Arial', 20)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                particleDisplays.append(ParticleDisplay(event.pos, Color((205, 0, 255), 5), Shape.RANDOM_POLYGON, 100, 20, 5))
        window.fill((255, 255, 255))
        #display fps
        fps = font.render(str(int(clock.get_fps())), True, (0, 0, 0))
        window.blit(fps, (10, 10))

        for particleDisplay in particleDisplays:
            particleDisplay.draw(window, clock.get_time())
        pygame.display.update()
        clock.tick(60)