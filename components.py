import pygame, win32clipboard
from componentsystem import Component

pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont("Arial", 20)

class ProgressBar(Component):
    def __init__(self, location: tuple[int, int], 
                 size: tuple[int, int], value: int = 0, max_value: int = 100,
                 bar_color: tuple[int, int, int] = (0, 255, 0),
                 background_color: tuple[int, int, int] = (255, 255, 255),
                 border_color: tuple[int, int, int] = (0, 0, 0),
                 border_radius: int = 0, text_display: bool = False, text_color: tuple[int, int, int] = (0, 0, 0),
                 text_font: pygame.font.Font = DEFAULT_FONT):
        
        super().__init__(location, size)
        self.value = value
        self.max   = max_value
        self.bar_color = bar_color
        self.background_color = background_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.text_display = text_display
        self.text_color = text_color
        self.text_font = text_font

    def draw(self, surface: pygame.Surface, environment: dict):
        self.value = max(0, min(self.value, self.max))
        pygame.draw.rect(surface, self.border_color, (self.location[0], self.location[1], self.size[0], self.size[1]), border_radius=self.border_radius)
        pygame.draw.rect(surface, self.background_color, (self.location[0] + 1, self.location[1] + 1, self.size[0] - 2, self.size[1] - 2), border_radius=self.border_radius)
        pygame.draw.rect(surface, self.bar_color, (self.location[0] + 1, self.location[1] + 1, (self.size[0] - 2) * (self.value / self.max), self.size[1] - 2), border_radius=self.border_radius)

        if self.text_display:
            # draw the text in the center of the bar
            text = self.text_font.render(f"{int(self.value)}/{int(self.max)}", True, self.text_color)
            surface.blit(text, (self.location[0] + (self.size[0] / 2) - (text.get_width() / 2), self.location[1] + (self.size[1] / 2) - (text.get_height() / 2)))

class TextDisplay(Component):
    def __init__(self, location: tuple[int, int], text: str,
                 font: pygame.font.Font = DEFAULT_FONT, color: tuple[int, int, int] = (0, 0, 0)):
        super().__init__(location, (0, 0))
        self.text = text
        self.font = font
        self.color = color

    def setText(self, text: str):
        self.text = text
    
    def draw(self, surface: pygame.Surface, environment: dict):
        surface.blit(self.font.render(self.text, True, self.color), self.location)

class ImageDisplay(Component):
    def __init__(self, location: tuple[int, int], image: pygame.Surface):
        super().__init__(location, (0, 0))
        self.image = image
    
    def draw(self, surface: pygame.Surface, environment: dict):
        surface.blit(self.image, self.location)

class TextInput(Component):
    def __init__(self, location: tuple[int, int], size: tuple[int, int], text: str = "",
                 font: pygame.font.Font = DEFAULT_FONT, color: tuple[int, int, int] = (0, 0, 0),
                 prompt_text: str = "Enter text...", prompt_color: tuple[int, int, int] = (200, 200, 200),
                 prompt_font: pygame.font.Font = DEFAULT_FONT,
                 border_radius: int = 0,
                 background_color: tuple[int, int, int] = (0, 0, 0),
                 text_color: tuple[int, int, int] = (255, 255, 255),
                 padding_left: int = 5, padding_right: int = 0,
                 padding_top: int = 0, padding_bottom: int = 0,
                 max_length: int = -1):

        super().__init__(location, size)
        self.EVENT_SYSTEM_HOOKED = True # Tells the event system to give this component events

        # Display config ===============================
        self.text  = text
        self.font  = font
        self.color = color
        self.prompt_text = prompt_text
        self.prompt_color = prompt_color
        self.prompt_font = prompt_font
        self.border_radius = border_radius
        self.background_color = background_color
        self.text_color = text_color
        self.padding_left = padding_left
        self.padding_right = padding_right
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.max_length = max_length

        self.CARET_BLINK_TIME = 500 # ms
        self._caret_blink_timer = 0
        self._caret_visible = True

        # Internal config ==============================
        self._selected = False
        self._keys_pressed = []

    
    def draw(self, surface: pygame.Surface, environment: dict):
        if self._caret_visible:
            self._caret_blink_timer -= environment["time_delta"]
            if self._caret_blink_timer <= 0:
                self._caret_blink_timer = self.CARET_BLINK_TIME
                self._caret_visible = False
        else:
            self._caret_blink_timer -= environment["time_delta"]
            if self._caret_blink_timer <= 0:
                self._caret_blink_timer = self.CARET_BLINK_TIME
                self._caret_visible = True

        pygame.draw.rect(surface, self.background_color, (self.location[0], self.location[1], self.size[0], self.size[1]), border_radius=self.border_radius)

        # if the padding is 0 on top and bottom, then the text will be centered
        if self.padding_top == 0 and self.padding_bottom == 0:
            textY = self.location[1] + (self.size[1] / 2) - (self.font.size(self.text)[1] / 2)
        else: textY = self.location[1] + self.padding_top

        # if the padding is 0 on left and right, then the text will be centered
        if self.padding_left == 0 and self.padding_right == 0: 
            textX = self.location[0] + (self.size[0] / 2) - (self.font.size(self.text)[0] / 2)
        else: textX = self.location[0] + self.padding_left

        visableText = self.text
        if self._selected and self._caret_visible:
            visableText += "|"
        else: visableText += " " # stop the text from jumping around when the caret is not visible
        while self.font.size(visableText)[0] > self.size[0] - self.padding_left - self.padding_right:
            # trim a chracter off the front of the text
            visableText = visableText[1:]

        if self.text.strip() == "" and not self._selected:
            surface.blit(self.font.render(self.prompt_text, True, self.prompt_color), (textX, textY))
        else:
            surface.blit(self.font.render(visableText, True, self.text_color), (textX, textY))

    def onEvent(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.location[0] <= event.pos[0] <= self.location[0] + self.size[0] and self.location[1] <= event.pos[1] <= self.location[1] + self.size[1]:
                self._selected = True
            else:
                self._selected = False

        if event.type == pygame.KEYDOWN:
            if self._selected:
                # check if ctrl and v are pressed
                if pygame.K_LCTRL in self._keys_pressed and event.key == pygame.K_v:
                    # get the text from the clipboard
                    win32clipboard.OpenClipboard()
                    self.text += win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    if self.max_length != -1 and len(self.text) > self.max_length:
                        self.text = self.text[:self.max_length]
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.max_length == -1 or len(self.text) < self.max_length:
                        self.text += event.unicode
                if event.key not in self._keys_pressed:
                    self._keys_pressed.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in self._keys_pressed:
                self._keys_pressed.remove(event.key)

class Button(Component):
    def __init__(self, location: tuple[int, int], size: tuple[int, int], text: str = "",
                 font: pygame.font.Font = DEFAULT_FONT, color: tuple[int, int, int] = (255, 255, 255),
                 background_color: tuple[int, int, int] = (0, 0, 0),
                 hover_background_color: tuple[int, int, int] = (0, 0, 0),
                 border_radius: int = 0,
                 padding_left: int = 0, padding_right: int = 0,
                 padding_top: int = 0, padding_bottom: int = 0,
                 on_click: callable = lambda: None):
        super().__init__(location, size)
        self.EVENT_SYSTEM_HOOKED = True # Tells the event system to give this component events

        self.text = text
        self.font = font
        self.color = color
        self.background_color = background_color
        self.border_radius = border_radius
        self.padding_left = padding_left
        self.padding_right = padding_right
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.hover_background_color = hover_background_color
        self.on_click = on_click

        self._hovered = False

    def draw(self, surface: pygame.Surface, environment: dict):
        pygame.draw.rect(surface, (self.background_color if not self._hovered else self.hover_background_color), (self.location[0], self.location[1], self.size[0], self.size[1]), border_radius=self.border_radius)

        # if the padding is 0 on top and bottom, then the text will be centered
        if self.padding_top == 0 and self.padding_bottom == 0:
            textY = self.location[1] + (self.size[1] / 2) - (self.font.size(self.text)[1] / 2)
        else: textY = self.location[1] + self.padding_top

        # if the padding is 0 on left and right, then the text will be centered
        if self.padding_left == 0 and self.padding_right == 0: 
            textX = self.location[0] + (self.size[0] / 2) - (self.font.size(self.text)[0] / 2)
        else: textX = self.location[0] + self.padding_left

        surface.blit(self.font.render(self.text, True, self.color), (textX, textY))

    def onEvent(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (self.location[0] <= event.pos[0] <= self.location[0] + self.size[0] 
                and self.location[1] <= event.pos[1] <= self.location[1] + self.size[1]):
                self.on_click()

        elif event.type == pygame.MOUSEMOTION:
            self._hovered = (self.location[0] <= event.pos[0] <= self.location[0] + self.size[0] 
                             and self.location[1] <= event.pos[1] <= self.location[1] + self.size[1])