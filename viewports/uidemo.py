import pygame
from componentsystem import Viewport, Component
from components import *

class UiDemo(Viewport):
    def __init__(self):
        super().__init__()

        # Create components
        self.progbar = ProgressBar((10, 10), (100, 20), 50)
        self.fpsDisplay = TextDisplay((10, 40), (100, 20), "FPS: 0", pygame.font.SysFont("Arial", 20))
        self.TextInput = TextInput((10, 70), (100, 20))
        self.testButton = Button((10, 100), (100, 20), "Test Button")
        self.testButton.on_click = lambda: print("Button clicked!")
        self.registerComponent(self.progbar)
        self.registerComponent(self.fpsDisplay)
        self.registerComponent(self.TextInput)
        self.registerComponent(self.testButton)
        self.barMoving = False
    
    def draw(self, enviorment: dict):
        super().draw(enviorment)

        if self.barMoving:
            self.progbar.value += 0.1 * enviorment["time_delta"]
        else:
            self.progbar.value -= 0.1 * enviorment["time_delta"]

        if self.progbar.value >= self.progbar.max:
            self.barMoving = False
        elif self.progbar.value <= 0:
            self.barMoving = True

        self.fpsDisplay.setText("FPS: " + str(int(enviorment["clock"].get_fps())))        