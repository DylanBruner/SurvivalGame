import pygame

class Component:
    def __init__(self, location: tuple[int, int], size: tuple[int, int]):
        self.location = location
        self.size     = size
        self.EVENT_SYSTEM_HOOKED = False
    
    def draw(self, surface: pygame.Surface, enviorment: dict):
        pass

    def onEvent(self, event: pygame.event.Event):
        pass

class Viewport:
    def __init__(self):
        self.components: list[Component] = []
        self.customCursor: pygame.Surface = None
        self.components = {
            'components': [],
            'hooks': {}
        }
        self.theme: Theme = Theme()

        self._customCursorEnabled = False
    
    def registerComponent(self, component: Component):
        if component.EVENT_SYSTEM_HOOKED:
            self.components['hooks'][component] = component.onEvent
        if self.theme != None:
            self.theme.apply(component)
        self.components['components'].append(component)

    def registerUnthemedComponent(self, component: Component):
        if component.EVENT_SYSTEM_HOOKED:
            self.components['hooks'][component] = component.onEvent
        self.components['components'].append(component)
    
    def unregisterComponent(self, component: Component):
        if component.EVENT_SYSTEM_HOOKED:
            del self.components['hooks'][component]
        self.components['components'].remove(component)
    
    def setCursor(self, cursor: pygame.Surface):
        surf = pygame.Surface(cursor.get_size(), pygame.SRCALPHA) # this might not actually do anything / be needed 
        surf.blit(cursor, (0, 0))
        self.customCursor = surf
    
    def setCustomCursorEnabled(self, enabled: bool):
        self._customCursorEnabled = enabled
        pygame.mouse.set_visible(not enabled)
    
    def draw(self, enviorment: dict):
        for component in self.components['components']:
            component.draw(enviorment["window"], enviorment)
        if self._customCursorEnabled:
            enviorment["window"].blit(self.customCursor, pygame.mouse.get_pos())
        
    def onEvent(self, event: pygame.event.Event):
        for component in self.components['hooks']:
            component.onEvent(event)

class Theme:
    def __init__(self):
        self.THEME_TREE = {
            'ProgressBar': {
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
        if component.__class__.__name__ in self.THEME_TREE:
            for key in self.THEME_TREE[component.__class__.__name__]:
                if hasattr(component, key):
                    setattr(component, key, self.THEME_TREE[component.__class__.__name__][key])
                else:
                    print(f"Warning: {component.__class__.__name__} does not have attribute {key}.")