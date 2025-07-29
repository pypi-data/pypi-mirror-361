from ursina import *





app = Ursina()


# Entity(model='cube', scale=(16,.1,16))

from ursina.prefabs.primitives import *

camera.far = 100

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *

#place the camera
base.trackball.node().setPos(0, 15, 1)
base.trackball.node().setHpr(0, 40, 0)

#the shaders...
#vertex shader:
v_shader='''#version 140

            struct p3d_LightSourceParameters {
              vec4 color;
              vec3 spotDirection;
              sampler2DShadow shadowMap;
              mat4 shadowViewMatrix;

            };

            uniform p3d_LightSourceParameters my_light;
            uniform mat4 p3d_ModelViewProjectionMatrix;
            uniform mat3 p3d_NormalMatrix;
            uniform mat4 p3d_ModelViewMatrix;

            in vec4 p3d_Vertex;
            in vec3 p3d_Normal;
            in vec2 p3d_MultiTexCoord0;

            out vec2 uv;
            out vec4 shadow_uv;
            out vec3 normal;

            void main()
                {
                //position
                gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                //normal
                normal = p3d_NormalMatrix * p3d_Normal;
                //uv
                uv = p3d_MultiTexCoord0;
                //shadows
                shadow_uv = my_light.shadowViewMatrix * (p3d_ModelViewMatrix * p3d_Vertex);
                }'''
#fragment shader
f_shader='''#version 140

        struct p3d_LightSourceParameters {
          vec4 color;
          vec3 spotDirection;
          sampler2DShadow shadowMap;
          mat4 shadowMatrix;
        };

        uniform p3d_LightSourceParameters my_light;
        uniform sampler2D p3d_Texture0;
        uniform vec3 camera_pos;
        uniform float shadow_blur;

        in vec2 uv;
        in vec4 shadow_uv;
        in vec3 normal;

        out vec4 color;

        float textureProjSoft(sampler2DShadow tex, vec4 uv, float bias, float blur)
            {
            float result = textureProj(tex, uv, bias);
            result += textureProj(tex, vec4(uv.xy + vec2( -0.326212, -0.405805)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(-0.840144, -0.073580)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(-0.695914, 0.457137)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(-0.203345, 0.620716)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.962340, -0.194983)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.473434, -0.480026)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.519456, 0.767022)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.185461, -0.893124)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.507431, 0.064425)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(0.896420, 0.412458)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(-0.321940, -0.932615)*blur, uv.z-bias, uv.w));
            result += textureProj(tex, vec4(uv.xy + vec2(-0.791559, -0.597705)*blur, uv.z-bias, uv.w));
            return result/13.0;
            }

        void main()
            {
            //base color
            vec3 ambient=vec3(0.1, 0.1, 0.2);
            //texture
            vec4 tex=texture(p3d_Texture0, uv);
            //light ..sort of, not important
            vec3 light=vec3(0,0,0);

            //shadows
            //float shadow= textureProj(my_light.shadowMap,shadow_uv); //meh :|
            float shadow= textureProjSoft(my_light.shadowMap, shadow_uv, 0.0001, shadow_blur);//yay! :)

            //make the shadow brighter
            shadow=0.5+shadow*0.5;

            color=vec4(tex.rgb*(light*shadow+ambient), tex.a);

            }'''
shader = Shader.make(Shader.SL_GLSL,v_shader, f_shader)

#make some floor
cm = CardMaker('')
cm.set_frame(-10, 10, -10, 10)
floor=render.attach_new_node(cm.generate())
floor.set_p(-90)
#set a texture
floor.set_texture(loader.load_texture('maps/grid.rgb'))
floor.set_shader(shader)

#load some model
panda=Actor('panda-model', {'walk': 'panda-walk4'})
panda.reparent_to(render)
panda.set_scale(0.005)
panda.loop('walk')
panda.set_shader(shader)

#light
my_light = render.attach_new_node(DirectionalLight("Spot"))
my_light.node().set_shadow_caster(True, 512, 512)
my_light.node().set_color((0.9, 0.9, 0.8, 1.0))
#my_light.node().showFrustum()
my_light.node().get_lens().set_fov(40)
my_light.node().get_lens().set_near_far(0.1, 30)
render.setLight(my_light)
my_light.set_pos(-20, 0, 20)
my_light.look_at(0, 0, 0)
render.set_shader_input('my_light',my_light)
render.set_shader_input('shadow_blur',0.2)


def set_softness():
    v=float(slider['value'])
    render.set_shader_input('shadow_blur', v)

slider = DirectSlider(range=(0, 0.5), value=0.2, scale=0.5, pos=(-0.8,0.0,0.9), command=set_softness)


EditorCamera()

RedCube(x=2, shader=shader)
GreenSphere(y=2, shader=shader)

app.run()
