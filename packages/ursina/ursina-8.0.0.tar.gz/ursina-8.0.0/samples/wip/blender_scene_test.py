from ursina import *


app = Ursina()
from ursina.shaders import normals_shader

desert_scene = load_blender_scene('blender_level_editor_test_scene_2')
# desert_scene.Cube.color=color.red
desert_scene.Cube.shader = normals_shader

EditorCamera()


def update():
    desert_scene.Cube.x += (held_keys['d'] - held_keys['a']) * time.dt * 10
    desert_scene.Cube.rotation_x += 1
    desert_scene.Cube.rotation_y += 1
    desert_scene.Cube.rotation_z += 1

app.run()
