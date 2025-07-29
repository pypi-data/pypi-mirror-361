from ursina import *

app = Ursina(forced_aspect_ratio=16/9, editor_ui_enabled=False)
window.color = color.black
camera.fov = 90
text = Text('press space to start', origin=[0,0])

outer_shape = Entity(model=Cylinder(16, mode='line', thickness=1), color=color.azure, scale=80, scale_y=16, x=-20, y=-5, enabled=False)
inner_shape = Entity(parent=outer_shape, model=Cylinder(16, mode='line', thickness=1), scale=.25, scale_y=1, color=outer_shape.color)

playing = False

def input(key):
    global playing

    if not playing and key == 'space':
        playing = True
        text.enabled = False
        outer_shape.enabled = True

def update():
    if playing:
        outer_shape.rotation_y += 1
        outer_shape.rotation_x -= .05

app.run()
