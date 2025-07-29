from ursina import *
from copy import copy
from ursina.shaders import triplanar_shader

app = Ursina()
rocks = (load_model('procedural_rock_0'), load_model('procedural_rock_0'))
# rocks = ('cube', 'sphere')

# rock_0 = Entity(model='procedural_rock_0', eternal=True, visible=False)
# rock_1 = Entity(model='procedural_rock_1', eternal=True, visible=False)
# rock_0.model.colorize(color.light_gray, color.dark_gray, color.smoke, color.dark_gray, color.light_gray, color.dark_gray)
# rock_1.model.colorize(color.light_gray, color.dark_gray, color.smoke, color.dark_gray, color.light_gray, color.dark_gray)
# rock_entities = (rock_0, rock_1)
top_texture = load_texture('grass')._texture
rock_parent = Entity(eternal=True)
ground_plane = Entity(model='cube', origin_y=.5, scale=30, scale_y=1, texture='magic_tree_ground', color=color.white, eternal=True, shader=triplanar_shader)
ground_plane.set_shader_input('top_texture', top_texture)

def generate(seed=0):
    scene.clear()
    random.seed(seed)

    for i in range(8):
        e = Entity(
            parent = rock_parent,
            name = 'rock',
            # model = 'sphere',
            model = copy(random.choice(rocks)),
            # model = copy(random.choice(rock_entities).model),
            # origin_y = -.5,
            x = random.uniform(-10, 10),
            z = random.uniform(-10, 10),
            rotation = Vec3(random.uniform(0,360), random.uniform(0,360), random.uniform(0,360)),
            texture='magic_tree_ground',
            shader = triplanar_shader,
            )
        e.set_shader_input('top_texture', top_texture)
        e.set_shader_input('transform_matrix', e.getNetTransform().getMat())
        # e.scale *= distance(e, ground_plane) * .5
        # e.model.colors = (color.random_color(),) * len(e.model.vertices)
        # e.model.generate()
        e.scale = abs(lerp(10, 1, distance(e, ground_plane)/10) * .3)
        e.scale *= 2
        # e.scale *= abs(e.x * e.z) *.1
        # e.color = color.dark_gray.tint(random.uniform(-.1,.1))


# generate()

seed = 0
rotation_seed = 0

def input(key):
    global seed, rotation_seed, rock_parent

    if key == 'space':
        generate(seed)
        seed += 1

    if key == 'r':
        rotation_seed += 1
        random.seed(rotation_seed)
        for e in rock_parent.children:
            e.rotation = Vec3(random.uniform(0,350), random.uniform(0,350), random.uniform(0,350))

    if key == 'c':
        rock_parent.combine()
        print('combined!')

        rock_parent.texture = 'brick'
        rock_parent.shader = triplanar_shader
        rock_parent.set_shader_input('top_texture', load_texture('shore')._texture)
        # print(rock_parent.model.normals)

    if key == 'k':
        # rock_parent.model.colorize()
        side_color = color.color(44,.43,.16)
        # side_color = color.black
        for e in rock_parent.children:
            # print(e)
            e.model.colorize(
                side_color, side_color,
                side_color.tint(-.2), color.white,
                side_color, side_color,
                smooth=False)
            cols = list()

def update():
    if held_keys['a']:
        rock_parent.children[0].rotation_x += 2
        rock_parent.children[0].rotation_y += 2
        rock_parent.children[0].set_shader_input('transform_matrix', rock_parent.children[0].getNetTransform().getMat())

            # world_normals = get_world_normals(e.model)
            # for n in world_normals:
            #     if n[1] > .3:
            #         cols.append(color.white)
            #     else:
            #         cols.append(side_color)
            #
            # e.model.colors = cols
            # e.model.generate()

m = Cylinder(8)
m.colorize()
wn = get_world_normals(m)
print(wn)
Entity(model=m)

EditorCamera()

# e = Entity(model='procedural_rock_0')
# e.model.colorize(color.light_gray, color.dark_gray, color.dark_gray, color.smoke, color.light_gray, color.dark_gray)

app.run()
