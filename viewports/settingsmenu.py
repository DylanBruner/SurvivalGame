from components.components import *
from components.componentsystem import Viewport
from util.myenvironment import Environment
from util.utils import Util
from game.misc.sounds import Sounds
from game.misc.lang import Lang

class SettingsMenu(Viewport):
    def __init__(self, size: tuple[int, int], environment: Environment):
        super().__init__(size, environment)
        self.setup()
    
    @Util.MonkeyUtils.autoErrorHandling
    def setup(self):
        self.lang = Lang()

        self.setCursor(Util.loadSpritesheet("data/assets/pointer.bmp", (18, 18), 1, transparentColor=(69, 78, 91))[0])
        self.setCustomCursorEnabled(True)

        # back button in the bottom left
        self.back_button = Button((5, self.size[1] - 45), (200, 40), self.lang.get(Lang.MENU_ACTION_BACK))
        self.back_button.on_click = lambda: (Sounds.playSound(Sounds.MENU_CLICK), Util.backViewport( self.environment))
        
        
        self.registerComponents([self.back_button])
    
    @Util.MonkeyUtils.autoErrorHandling
    def draw(self, environment: dict):
        super().draw(environment)

VIEWPORT_CLASS = SettingsMenu