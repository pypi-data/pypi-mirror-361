from ursina import *
from PIL import Image


app = Ursina()

window.color=color.black
size = (1920//8, 1080// 8)
print(size)
screen = Texture(Image.new(mode='RGBA', size=size, color=(0, 128, 128, 255)))
screen.filtering = None

e = Entity(parent=camera.ui, model='quad', texture=screen)
pos = 0


def input(key):
    if key == 'space':
        render()

def update():
    if held_keys['space']:
        render()
        global pos
        pos += 1


def render():
    for y in range(size[1]):
        for x in range(size[0]):
            screen.set_pixel(x,y, color.random_color())

    screen.apply()


app.run()
