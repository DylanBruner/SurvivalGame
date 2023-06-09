import pygame

class Component:
    """
    Base class for all components, no code to really comment here
    """
    def __init__(self, location: tuple[int, int], size: tuple[int, int]):
        self.location = location
        self.size     = size
        self.EVENT_SYSTEM_HOOKED = False
        self.priority = 0 # Doesn't matter
    
    def draw(self, surface: pygame.Surface, environment: dict):
        pass

    def onEvent(self, event: pygame.event.Event):
        pass

class Viewport:
    """
    Base class for all viewports, should be inherited from and not used directly
    """
    def __init__(self, size: tuple[int, int], environment):
        self.size = size
        self.environment = environment
        self.components: list[Component] = []
        self.customCursor: pygame.Surface = None
        self.components = {
            'components': [],
            'hooks': {}
        }
        self.closed = False
        self.theme: Theme = Theme()

        self._customCursorEnabled = False
    
    def registerComponent(self, component: Component, theme_overrides: dict[str, any] = None):
        if component.EVENT_SYSTEM_HOOKED:
            self.components['hooks'][component] = component.onEvent
        if self.theme != None:
            self.theme.apply(component)
        if theme_overrides != None: Theme.cApply(component, theme_overrides)
            
        self.components['components'].append(component)
        
    def registerComponents(self, components: list[Component]):
        for component in components: self.registerComponent(component)

    def registerUnthemedComponent(self, component: Component):
        if component.EVENT_SYSTEM_HOOKED:
            self.components['hooks'][component] = component.onEvent
        self.components['components'].append(component)
    
    def unregisterComponent(self, component: Component):
        if component.EVENT_SYSTEM_HOOKED:
            del self.components['hooks'][component]
        self.components['components'].remove(component)
    
    def unregisterComponents(self, components: list[Component]):
        for component in components: self.unregisterComponent(component)
    
    def setCursor(self, cursor: pygame.Surface):
        surf = pygame.Surface(cursor.get_size(), pygame.SRCALPHA) # this might not actually do anything / be needed 
        surf.blit(cursor, (0, 0))
        self.customCursor = surf
    
    def setCustomCursorEnabled(self, enabled: bool):
        """
        Toggle the custom cursor
        """
        self._customCursorEnabled = enabled
        pygame.mouse.set_visible(not enabled)
    
    def draw(self, environment: dict):
        for component in self.components['components']:
            component.draw(environment["window"], environment)

        if self._customCursorEnabled: # draw the custom cursor if it's enabled
            environment["window"].blit(self.customCursor, pygame.mouse.get_pos())
        
    def setup(self) -> None:
        """
        Should be where the components are registered, not in __init__ because setup is
        called when the viewport is reloaded / resized
        """
        ...
    
    def reload(self) -> None:
        self.components['components'] = []
        self.components['hooks'] = {}
        self.setup()
    
    # Should be handled by each viewport but we can add some basic default behavior here
    def resize(self, old: tuple[int, int], new: tuple[int, int]):
        self.size = new
        self.components['components'] = []
        self.components['hooks'] = {}
        self.setup()
        
    def onEvent(self, event: pygame.event.Event):
        for component in self.components['hooks']:
            component.onEvent(event)
        
class Theme:
    """
    System for applying themes to components instead of individually setting attributes
    """
    def __init__(self):
        self.THEME_TREE = {
            'ProgressBar': { # <=== Class Name, v=== Attributes
                'background_color': (44, 51, 51),
                'border_color': (44, 51, 51),
                'border_radius': 4,
                'bar_color': (255, 255, 255),
            },
            'TextDisplay': {
                'color': (0, 0, 0),
            },
            'TextInput': {
                'background_color': (44, 51, 51),
                'border_radius': 4,
            },
            'Button': {
                'background_color': (44, 51, 51),
                'hover_background_color': (22, 25, 25),
                'color': (255, 255, 255),
                'border_radius': 4,
            }
        }
        
    def apply(self, component: Component) -> None:
        """
        Litterally just applies the theme to the component, not much else to say
        """
        if component.__class__.__name__ in self.THEME_TREE:
            for key in self.THEME_TREE[component.__class__.__name__]:
                if hasattr(component, key):
                    setattr(component, key, self.THEME_TREE[component.__class__.__name__][key])
                else:
                    print(f"Warning: {component.__class__.__name__} does not have attribute {key}.")

    @staticmethod
    def cApply(component: Component, tree: dict[str, any]) -> None:
        """
        I belive this stood for custom apply, 
        but I'm not sure as I'm commenting this a few weeks after writing it
        """
        for key in tree:
            if hasattr(component, key):
                setattr(component, key, tree[key])
            else:
                print(f"Warning: {component.__class__.__name__} does not have attribute {key}.")