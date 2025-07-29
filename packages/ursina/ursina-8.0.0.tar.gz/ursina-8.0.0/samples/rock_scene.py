from ursina import *



app = Ursina()
Texture.default_filtering = 'trilinear'
# application.asset_folder = Path('C:/sync/3d')
from ursina.shaders import lit_with_shadows_shader

# from ursina.shaders import matcap_shader
# Entity(model='rock_scene', shader=matcap_shader, texture='shore')



from ursina.shaders import triplanar_shader
triplanar_shader.default_input['side_texture'] = load_texture('grass', application.internal_textures_folder)
triplanar_shader.default_input['side_texture_scale'] = Vec2(1/10,1/10)

e = Entity(model='floating_isle', shader=triplanar_shader, texture='brick', texture_scale=Vec2(.1))
EditorCamera()

# PointLight(y=3)
sun = DirectionalLight(y=50, rotation_x=120-90)
# sun._light.get_lens().set_near_far(0,30)
#
# sun._light.show_frustum()
def input(key):
    if key == 'escape':
        quit()


app.run()
