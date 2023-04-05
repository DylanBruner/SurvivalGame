import pygame, importlib, inspect
from componentsystem import Viewport
from myenvironment import Environment

class Util:
    @staticmethod
    def loadSpritesheet(path: str, spriteSize: tuple, spriteCount: int, transparentColor: tuple = None):
        spritesheet = pygame.image.load(path).convert_alpha()
        if transparentColor:
            spritesheet.set_colorkey(transparentColor)
        sprites = []
        for i in range(spriteCount):
            sprites.append(spritesheet.subsurface((i * spriteSize[0], 0, spriteSize[0], spriteSize[1])))
        return sprites

    @staticmethod
    def launchViewport(old: Viewport, new: Viewport, enviorment: Environment) -> None:
        old.setCustomCursorEnabled(False)
        enviorment.viewport = new
        enviorment.last_viewports.append(old)
    
    @staticmethod
    def backViewport(enviorment: Environment) -> None:
        old = enviorment.viewport
        new = enviorment.last_viewports.pop()
        old.setCustomCursorEnabled(False)
        enviorment.viewport = new
    
    @staticmethod
    def distance(p1: tuple, p2: tuple) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    @staticmethod
    def getTileLocation(mouse_pos: tuple, player_pos: tuple, window_size: tuple, tile_size: int) -> tuple:
        startX = player_pos[0] - (window_size[0] // tile_size) // 2
        startY = player_pos[1] - (window_size[1] // tile_size) // 2
        return ((mouse_pos[0] // tile_size) + startX, (mouse_pos[1] // tile_size) + startY)

    @staticmethod
    def gameTimeToNice(gameTime: int) -> str: #00:00 AM/PM
        gameTime = int(gameTime)
        hours = gameTime // 60
        minutes = gameTime % 60
        if hours > 12:
            hours -= 12
            ampm = "PM"
        else:
            ampm = "AM"
        # round hours and minutes to 2 digits
        hours = str(hours).zfill(2)
        minutes = str(minutes).zfill(2)
        return f"{hours}:{minutes} {ampm}"

    class MonkeyUtils:
        RELOAD_BLACKLIST = ["pygame"]

        @staticmethod
        def reloadModules(globs: dict):
            for key, value in globs.items():
                if type(value) == type(importlib) and key not in Util.MonkeyUtils.RELOAD_BLACKLIST:
                    importlib.reload(value)

        @staticmethod
        def getViewportFromName(name: str):
            module = importlib.import_module(f"viewports.{name}")
            if not hasattr(module, "VIEWPORT_CLASS"):
                raise AttributeError(f"Module {name} does not have a VIEWPORT_CLASS attribute")
            return getattr(module, "VIEWPORT_CLASS")
        
        @staticmethod
        def reload(environment: Environment, globs: dict):
            Util.MonkeyUtils.reloadModules(globs)
            environment.window = pygame.display.set_mode(environment.window.get_size())
            # print(environment.viewport.__class__.__name__)
            # get the parent module of the viewport
            module = inspect.getmodule(environment.viewport).__name__.split(".")[-1]
            environment.viewport = Util.MonkeyUtils.getViewportFromName(module)(environment.window.get_size(), environment)

if __name__ == "__main__":
    Util.MonkeyUtils.getViewportFromName("mainmenu")