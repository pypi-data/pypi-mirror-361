from ursina import *




# app = Ursina()
#
#
# Entity(model='cube', scale=8, collider='box')
#
#
# sphere = Entity(model='sphere', scale=10, collider='sphere')
#
# EditorCamera()
#
#
# def input(key):
#     if key == 'left mouse down' and mouse.point:
#         e = Entity(model='cube', scale=.5, color=color.gray, position=mouse.world_point)
#         # print(mouse.world_normal, mouse.collision)
#         e.look_at(e.position + mouse.world_normal)
#
#     if key == 'f':
#         sphere.model.colorize()
#         for i, v in enumerate(sphere.model.vertices):
#             # print(v)
#             # e = Entity(parent=sphere.model, model='cube', world_scale=.5, color=color.gray, position=v, add_to_scene_entities=False)
#             # e.look_at(e.position + sphere.model.normals[i])
#             # e.world_parent = scene
#             # sphere.model.colors[i] = color.random_color()
#             sphere.model.colors[i] = color.black
#
#             ray = raycast(v + sphere.model.normals[i], sphere.model.normals[i], debug=True)
#             if not ray.hit:
#                 sphere.model.colors[i] = color.white
#
#
#
#         sphere.model.generate()
#
#
app = Ursina()

ray = Entity()
def hit_sphere(center, radius, ray):
    oc = ray.position - center
    a = dot(r.forward, r.forward)
    b = 2 * dot(oc, r.forward)


t = Entity(parent=camera.ui, model='quad', texture='brick').texture
t.filtering = False
print(t)

def render():
    i = time.time()

    lower_left_corner = Vec3(-2, -1, -1)
    horizontal = Vec3(4, 0, 0)
    vertical = Vec3(0, 2, 0)
    origin = Vec3(0, 0, 0)

    for y in range(t.height):
        for x in range(t.width):
            col = lerp(color.red, color.yellow, x/t.width)
            col = lerp(col, color.azure, (y/t.height))
            t.set_pixel(x, y, col)

    t.apply()

    print(time.time() - i)


render()






app.run()
