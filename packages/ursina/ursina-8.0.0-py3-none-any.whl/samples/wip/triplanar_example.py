from ursina import *
from ursina.shaders import triplanar_shader


app = Ursina()

for z in range(0,1000, 100):
    e = Entity(model='rock_shape', shader=triplanar_shader, scale=32, texture='magic_tree_ground')
    e.set_shader_input('top_texture', load_texture('grass')._texture)

    e.z = z
    e.x = random.uniform(-100,100)
plane = Entity(model='plane', scale=9999, texture='grass')
scene.fog_density = .001
EditorCamera()
Sky(texture='sky_sunset')
app.run()
