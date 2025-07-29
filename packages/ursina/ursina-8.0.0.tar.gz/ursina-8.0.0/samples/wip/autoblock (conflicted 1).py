from ursina import *
from copy import copy



app = Ursina()

dummy = Entity(model='cube')

cube = Entity(model='cube')
cube.model.colorize()
cube = cube.model

ground_plane = Entity(model='plane', scale=32, origin=(-.5,0,-.5), position=(-.5,0,-.5), collider='box', color=color.azure)
cursor = Entity(model=Cube(mode='line'), origin_y=-.5, scale_y=8, color=color.red)
level = Entity(model=Mesh())
i = 0


for z in range(32):
    for x in range(32):
        level.model.vertices += [Vec3(*v) + Vec3(x,0,z) for v in cube.vertices]
        level.model.triangles += [v for v in cube.triangles]
        level.model.colors += [v for v in cube.colors]

level.model.generate()


def update():
    if mouse.hovered_entity == ground_plane:
        cursor.world_position = mouse.world_point
        cursor.world_x = int(cursor.world_x)
        cursor.world_z = int(cursor.world_z)


def on_click():
    x, y = int(cursor.world_x), int(cursor.world_z)
    print(x,y)

ground_plane.on_click = on_click

EditorCamera()
app.run()
