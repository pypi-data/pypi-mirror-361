from panda3d.core import Shader


empty_shader = Shader.make(Shader.SL_GLSL,
vertex='''
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;
}
''',

fragment='''
#version 130

uniform sampler2D p3d_Texture0;
in vec2 texcoord;
out vec4 fragColor;


void main() {
    // gl_FragColor.rgb = vec3(0,1,1);
    vec4 color = texture(p3d_Texture0, texcoord);
    fragColor = color.rgba;
}


''', geometry='')


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='cube', color=color.orange)
    camera.shader = empty_shader
    EditorCamera()

    app.run()
