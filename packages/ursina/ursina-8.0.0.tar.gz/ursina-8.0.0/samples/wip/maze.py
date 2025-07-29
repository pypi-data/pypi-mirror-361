from ursina import *
from copy import copy


app = Ursina()

cube = load_model('cube', use_deepcopy=True)
cube.colorize(color.smoke, color.light_gray, color.dark_gray, color.white, color.smoke, color.light_gray)

# ground = Entity(model='plane', texture='white_cube', origin=(-.5,0,-.5), scale=20, texture_scale=(20,20), rotation_y=45)
ground = Entity(model=Plane((20,20)), scale=400, texture='grass', texture_scale=(10,10))
Sky()


# e = Entity(model=copy(cube), origin_y=-.5, scale=172, scale_y=10)
# e = Entity(model=copy(cube), origin_y=-.5, scale=126, scale_y=20)
#
# def input(key):
#     if key == 'space':
#         e.scale_x -= 2
#         print(e.scale_x)

t = time.time()
def make_maze():
    maze_parent = Entity(scale=10, position=(-100, 0, -100))
    goal_post = Entity(
        model=Cylinder(resolution=24),
        origin=(.25,0,.25),
        scale=16,
        scale_y=32,

        )
    # return
    i = 0
    for z in range(20):
        for x in range(20):
            if x > 6 and x < 13 and z > 6 and z < 13:
                continue
            #
            # if x < 8:
            #     x_lvl = x//2
            # elif x > 13:
            #     x_lvl = 20-x
            #
            # z_lvl = 10
            #
            # level = min(x_lvl, z_lvl)

            invoke(Entity,
                parent=maze_parent,
                model=copy(cube),
                # texture='white_cube',
                # collider='box',
                # color=color.light_gray,
                scale_x=.25,
                scale_z=1.65,
                origin_y=-.5,
                position=(x+random.uniform(-.01,.01), 0+random.uniform(-.01,.01), z+random.uniform(-.01,.01)),
                rotation_y=random.choice([45,-45]),
                delay=i
                )
            # invoke(eval, code, delay=i)
            i += .005

def input(key):
    if key == 'space':
        make_maze()

print(time.time() - t)

Entity(model='cube', color=color.red)
# camera.position = (0,400,-400)
# camera.look_at((0,0,0))
camera.z = -800
EditorCamera(rotation_x=45)

# from ursina.prefabs.first_person_controller import FirstPersonController
# player = FirstPersonController(speed=10)
#

# from ursina .shaders import camera_vertical_blur_shader
# camera.shader = camera_vertical_blur_shader
# camera.set_shader_input('blur_size', .05)
# slider = ThinSlider(max=.1, dynamic=True, position=(-.25, -.45))
#
# def set_blur():
#     camera.set_shader_input("blur_size", slider.value)
#
# slider.on_value_changed = set_blur

# player.enabled = False
# camera.position = (0,100,-200)
# camera.look_at((0,0,0))

# camera.animate_position(player.position + player.up, duration=4, curve=curve.linear)
# camera.animate_rotation(player.rotation, duration=10, curve=curve.out_expo)
# invoke(setattr, player, 'enabled', True, delay=4)

app.run()
