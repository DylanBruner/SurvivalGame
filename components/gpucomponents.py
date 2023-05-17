from gpu.gpucore import Surface
from vispy.scene.visuals import Image

class TestButton:
    def __init__(self, text: str, size: tuple[int, int], color: tuple[int, int, int], 
                 click_color: tuple[int, int, int], hover_color: tuple[int, int, int]):
        
        self._prop_text  = text
        self._prop_size  = size
        self._prop_color = color
        self._prop_click_color = click_color
        self._prop_hover_color = hover_color

        self._attr_hover     = False
        self._attr_click     = False
        self._attr_modified  = True
        self._attr_mouse_loc = (0, 0)

        self.surf = Surface(size)

        self._monk_parent = None
    
    def link(self, parent) -> 'TestButton':
        self._monk_parent = parent
        self._linked = Image(self.surf.getArray(), parent=parent.getScene())
        return self

    def remove(self, parent) -> 'TestButton':
        self._monk_parent = parent
        parent.getScene()._remove_child(self._linked)

    def updateSurface(self):
        if self._monk_parent is not None:
            self.remove(self._monk_parent)
        else:
            raise Exception("Cannot update surface without linking to a parent")
        
        self.surf.fill(self._prop_color)
        self.surf.rect((0, 0), self._prop_size, self._prop_color)
        self.surf.renderText(self._prop_text, (self._prop_size[1] // 2 - self.surf.getTextSize(self._prop_text, 20)[0] // 2,
                                                  self._prop_size[0] // 2 - self.surf.getTextSize(self._prop_text, 20)[1] // 2), 
                                                  20, (0, 0, 0, 255))
        
        self.link(self._monk_parent)
    
    def on_mouse_move(self, event):
        self._attr_mouse_loc = event.pos

        # check if mouse is hovering over button, note width and height are swapped
        if (self._attr_mouse_loc[0] >= self._prop_size[1] and self._attr_mouse_loc[0] <= self._prop_size[1] + self._prop_size[0]) and \
              (self._attr_mouse_loc[1] >= self._prop_size[0] and self._attr_mouse_loc[1] <= self._prop_size[0] + self._prop_size[1]):
            self._attr_modified = self._attr_hover != True
            self._attr_hover = True
            print("Mouse hovering over button")
        else:
            self._attr_modified = self._attr_hover != False
            self._attr_hover = False
            print("Mouse not hovering over button")