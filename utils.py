import pygame, importlib, inspect, sys, traceback, colorama, os
from componentsystem import Viewport
from myenvironment import Environment

_data = {
    "MonkeyUtils": {
        "auto_error_handling": {
            "enabled": True,
            "prefix": f"{colorama.Fore.RED}[MonkeyUtils/{colorama.Fore.LIGHTRED_EX}AutoErrorHandling{colorama.Fore.RED}]{colorama.Fore.RESET} ",
            "disabled_functions": []
        }
    }
}

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
    def loadSpritesheetAdvanced(path: str, spriteSize: tuple, spriteCount: int, spritesPerRow: int, transparentColor: tuple[int, int, int] = None) -> list[pygame.Surface]:
        spritesheet = pygame.image.load(path).convert_alpha()
        if transparentColor:
            spritesheet.set_colorkey(transparentColor)
        sprites = []
        for i in range(spriteCount):
            sprites.append(spritesheet.subsurface((i % spritesPerRow * spriteSize[0], i // spritesPerRow * spriteSize[1], spriteSize[0], spriteSize[1])))
        return sprites

    @staticmethod
    def launchViewport(old: Viewport, new: Viewport, enviorment: Environment) -> None:
        # old.setCustomCursorEnabled(False)
        enviorment.viewport = new
        enviorment.last_viewports.append(old)
    
    @staticmethod
    def backViewport(enviorment: Environment) -> None:
        old = enviorment.viewport
        new = enviorment.last_viewports.pop()
        # old.setCustomCursorEnabled(False)
        enviorment.viewport = new
    
    @staticmethod
    def distance(p1: tuple, p2: tuple) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

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
    
    @staticmethod
    def calculateStaminaCost(breaking_power: int) -> int:
        # higher breaking power = more stamina cost
        return max(1, breaking_power * 2 - 1)

    @staticmethod
    def shiftUnicode(chr: int) -> int:
        return chr + 0xE000

    @staticmethod
    def unshiftUnicode(chr: int) -> int:
        return chr - 0xE000

    class MonkeyUtils:
        RELOAD_BLACKLIST = ["pygame"]
        OTHER_RELOAD     = [file.replace(".py","") for file in os.listdir(".") if file.endswith(".py")]

        @staticmethod
        def getViewportFromName(name: str):
            module = importlib.import_module(f"viewports.{name}")
            if not hasattr(module, "VIEWPORT_CLASS"):
                raise AttributeError(f"Module {name} does not have a VIEWPORT_CLASS attribute")
            return getattr(module, "VIEWPORT_CLASS")

        @staticmethod
        def reloadModules(globs: dict):
            for module in list(sys.modules.keys()):
                if module not in Util.MonkeyUtils.RELOAD_BLACKLIST and (
                    module.startswith("viewports") or module.startswith("game") or module in Util.MonkeyUtils.OTHER_RELOAD):

                    importlib.reload(sys.modules[module])
                    globs[module.split(".")[-1]] = sys.modules[module]
        
        @staticmethod
        def reload(environment: Environment, globs: dict):
            _data["MonkeyUtils"]["auto_error_handling"]["disabled_functions"] = []
            # attempt to save the game
            if hasattr(environment, "viewport") and hasattr(environment.viewport, "save"):
                environment.viewport.save.save()
            try:
                Util.MonkeyUtils.reloadModules(globs)
            except Exception as e:
                if _data["MonkeyUtils"]["auto_error_handling"]["enabled"]:
                    traceback.print_exc()
                    print(_data["MonkeyUtils"]["auto_error_handling"]["prefix"] + f"Caught a error while reloading modules!")
            
            # reload the current viewport, all other should be reloaded when the modules are reloaded (hopefully)
            environment.window = pygame.display.set_mode(environment.window.get_size(), pygame.RESIZABLE)
            module = inspect.getmodule(environment.viewport).__name__.split(".")[-1]

            if module == "gameview":
                environment.viewport.save.save()
                environment.viewport = Util.MonkeyUtils.getViewportFromName(module)(environment.window.get_size(), environment, environment.viewport.save)                
            else:
                environment.viewport = Util.MonkeyUtils.getViewportFromName(module)(environment.window.get_size(), environment)
        
        @staticmethod
        def autoErrorHandling(func: callable):
            def wrapper(*args, **kwargs):
                if func.__name__ in _data["MonkeyUtils"]["auto_error_handling"]["disabled_functions"]:
                    return None
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # print the full error and traceback just like normal
                    traceback.print_exc()
                    print(_data["MonkeyUtils"]["auto_error_handling"]["prefix"] + f"Caught a error while calling {func.__name__}! (function will be disabled until next reload)")

                    if _data["MonkeyUtils"]["auto_error_handling"]["enabled"]:
                        _data["MonkeyUtils"]["auto_error_handling"]["disabled_functions"].append(func.__name__)
                    return None
            return wrapper

if __name__ == "__main__":
    Util.MonkeyUtils.getViewportFromName("mainmenu")