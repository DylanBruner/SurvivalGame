from gpu.gpucore import App
from components.gpucomponents import TestButton
from vispy.scene.visuals import Image

app = App((800, 600))
btn = TestButton("Hello", (50, 100), (255, 0, 0), (0, 255, 0), (0, 0, 255)).link(app)
btn.updateSurface()

app.connect(btn.on_mouse_move)

app.start()