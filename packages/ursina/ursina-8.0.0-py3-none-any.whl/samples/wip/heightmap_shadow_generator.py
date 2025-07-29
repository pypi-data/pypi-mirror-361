from ursina import *


e = Entity(parent=camera.ui, model='quad', texture='desert_terrain_heightmap')
t = e.texture


for y in range(t.height):
    for x in range(t.width):
        col = tex.get_pixel(x+1, y)
        
