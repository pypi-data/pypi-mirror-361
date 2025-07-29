from ursina import *

app = Ursina()
camera.orthographic = True


# building = Entity()

def make_building():
    # pass
    scene.clear()
#     # [destroy(e) ]
    # p = Entity(model=Cylinder(radius=radius, resolution=edges))
    # for i in range(0, 360, 360//edges):
    #     origin = Entity(parent=p, rotation_y = i)
    #     wall = Entity(parent=origin, model='cube', scale=(10,1,2), origin_z=-.5, origin_y=-.5, z=radius, color=color.orange.tint(random.uniform(-.2,.1)))
    #     column = Entity(parent=wall, model=Cylinder(8), x=.5, world_scale=(2,5,2), color=color.gold.tint(random.uniform(-.2,.1)))

    # line = Entity(parent=p, model='cube', origin_z=-.5, color=color.green)
    # line.look_at(column)
    # line.scale_z = distance(column.world_position, line.world_position)
    # line.rotation_y = 0

    floor = Entity(model=Cylinder(settings['edges'], radius=settings['radius']), color=color.gold)
    points = [v for v in floor.model.vertices if v[1] < .01 and v != (0,0,0)]
    for p in points:
        p = [round(e) for e in p]

    points = set(points)
    for p in points:
        Entity(
            model=Cylinder(8),
            scale=(settings['column_radius'],settings['column_height'],settings['column_radius']),
            color=color.azure,
            position=p,
            origin_z=.5
            )
    print(points)



settings = {
    'radius' : 10,
    'edges' : 5,
    'column_radius' : 3,
    'column_height' : 5,
    }

for i, (key, value) in enumerate(settings.items()):
    slider = Slider(.1, 20, default=value, step=.1, text=key, x=-.6, y=-.45+(i/20), name=key+'_slider', eternal=True)
    print(i)
    def modify():
        value = slider.value
        settings[key] = value
        make_building()

    slider.on_value_changed = modify

# b = Button('lol')
# print('.............', b.collider)
# def input(key):
#     if key == 'd':
#         print('lol')
#         # print(scene.entities)
#         # print()
#         scene.clear()
        # print('.............', b.collider)
        # print(scene.entities)
        # print()

EditorCamera()
make_building()
app.run()
