from ursina import *

from ursina.shaders import basic_lighting_shader, colored_lights_shader

app = Ursina()

Entity(model='procedural_rock_0', shader=colored_lights_shader)
EditorCamera()

app.run()
