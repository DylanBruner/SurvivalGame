import pygame, time

from components import *
from componentsystem import Viewport
from myenviorment import Environment
from utils import Util

class PauseMenu(Viewport):
    def __init__(self, size: tuple[int, int], enviorment: Environment):
        super().__init__(size, enviorment)
        self.setup()
    
    def setup(self):
        self.pause_text = TextDisplay(location=(10, 10), text="Paused")
        self.registerComponent(self.pause_text)
        self.resume_button = Button(location=(10, 30), size=(100, 30), text="Resume")
        self.resume_button.on_click = self.resume
        self.registerComponent(self.resume_button)
        self.exit_button = Button(location=(10, 70), size=(100, 30), text="Exit")
        self.exit_button.on_click = self.exit
        self.registerComponent(self.exit_button)
    
    def resume(self):
        self.closed = True
        self.enviorment['overlays'].remove(self)
    
    def exit(self):
        ...
    
    def draw(self, enviorment: dict):
        super().draw(enviorment)