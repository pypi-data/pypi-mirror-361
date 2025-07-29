from ursina import *

app = Ursina()
terrain = Terrain('desert_terrain_heightmap', skip=1)
e = Entity(model=terrain, scale=(20,5,20), color=color.red)

from ursina.shaders import basic_lighting_shader, normals_shader

# e.model.generate_normals()
e.shader = basic_lighting_shader
e.set_shader_input('transform_matrix', e.getNetTransform().getMat())

# scene.fog_density = .1

EditorCamera()

app.run()
