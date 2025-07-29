# half rim = 1 - saturate(dot(data.worldViewDir, s.Normal));
# rim = smoothstep(_RimMin, _RimMax, rim);
# #ifdef _USERIMMAP
#     rim *= s.RimIntensityMultiplier;
# #endif
# #ifdef _SUN_COLORED_RIM
#     _RimColor = _LightColor0 * 0.5;
# #endif
# gi.indirect.specular += _RimColor.rgb * rim * _RimColor.a;




from ursina import *

rim_shader = Shader(language=Shader.GLSL,
vertex = '''
#version 430
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uv;
in vec3 p3d_Normal;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ProjectionMatrix;
out vec3 view_normal;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  uv = p3d_MultiTexCoord0;
  view_normal = mat3(p3d_NormalMatrix) * p3d_Normal;
}
''',

fragment='''
#version 430

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 uv;
in vec3 view_normal;
out vec4 color;


void main() {
    vec4 map = texture(p3d_Texture0, uv) * p3d_ColorScale;
    vec3 rgb = 1 - view_normal * 1.;
    color = vec4(map.rgb + rgb.rgb, 1.0);
}

''',
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', shader=rim_shader, rotation_y=45, color=color.azure)

    EditorCamera()
    # def update():
    #     e.rotation_x += 1
    #     e.rotation_y += 1
    #     e.rotation_z += 1

    def input(key):
        if key == 'space':
            if e.shader:
                e.shader = None
            else:
                e.shader = rim_shader

    camera.orthographic = True
    camera.fov = 3
    app.run()
