fragment_code = fragment='''
#version 420
uniform float iTime;
in vec2 iResolution;

in vec2 fragCoord;
out vec4 fragColor;

void main()
{
    vec2 uv = fragCoord;
    vec3 col = 0.5 + 0.5*cos(uv.xyx+vec3(0,4,8));
    fragColor = vec4(col,1.0);
}
'''
from panda3d.core import Shader

camera_contrast_shader = Shader.make(Shader.SL_GLSL,
vertex='''
#version 420
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 fragCoord;


void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  fragCoord = p3d_MultiTexCoord0;
}
''',

fragment=fragment_code, geometry='')


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='quad', scale=3)
    e.shader = camera_contrast_shader

    t = 0
    frame = 0

    e.set_shader_input('iResolution', window.size)
    e.set_shader_input('iTime', t)
    e.set_shader_input('iFrame', frame)

    def update():
      global t, frame
      t += time.dt
      e.set_shader_input('iTime', t)

      frame += 1
      e.set_shader_input('iFrame', frame)


    EditorCamera()

    app.run()
