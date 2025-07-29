from ursina import *

app = Ursina()


Entity(model='plane', scale=10, texture='brick')
EditorCamera()

camera.y = 5
camera.look_at((0,0,0))

# filter
from panda3d.core import Shader
from direct.filter.FilterManager import FilterManager
from panda3d.core import Texture as PandaTexture

# manager = FilterManager(base.win, camera.ui_camera)
manager = FilterManager(base.win, base.cam)
tex = PandaTexture()
quad = manager.renderSceneInto(colortex=tex)
quad.setShader(Shader.load("projector_shader.sha"))
quad.setShaderInput("tex", tex)

quad.setShaderInput("projector_texture", load_texture('projector_texture')._texture)



app.run()
