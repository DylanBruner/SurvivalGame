import sys, time, numpy
from PIL import Image as img
from vispy import scene, app
from vispy.scene.visuals import Text, Image
from gpucore import gpuUTILS, Surface

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                            size=(800, 600), show=True)
canvas.show()

fpsText = Text("0", color='red', pos=(0, 0), parent=canvas.scene)
fpsText.font_size = 24
fpsText.pos = (200, 200)

rect = scene.visuals.Rectangle(center=(400, 400), width=100, height=100, parent=canvas.scene)
rect.color = 'red'

testImage = Surface((120, 120))
testImageRender = Image(testImage.getArray(), parent=canvas.scene)

frames = 0
lastTime = time.time()

def register(ev):
    global frames, lastTime
    canvas.update()

    frames += 1
    if time.time() - lastTime >= 1:
        fpsText.text = str(frames)
        frames = 0
        lastTime = time.time()
    
    # draw a rectangle

timer = app.Timer()
timer.connect(register)
timer.start(0)

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()