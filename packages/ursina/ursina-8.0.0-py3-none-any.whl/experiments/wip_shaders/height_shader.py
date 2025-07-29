from ursina import *; height_shader = Shader(language=Shader.GLSL, vertex = '''#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec2 uv;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv = vec2(.5, p3d_Vertex.y * p3d_MultiTexCoord0.y) + vec2(.5,.5);
}
''',
fragment='''
#version 130
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec3 base = texture2D( p3d_Texture0, uv ).rgb;
    fragColor = vec4( base, 1. ) * p3d_ColorScale;
}

''',
)



if __name__ == '__main__':
    '''
    use matcap textures
    '''
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    shader = height_shader

    a = WhiteCube(shader=shader, texture='matcap_4')
    b = WhiteSphere(shader=shader, rotation_y=180, x=3, texture='matcap_4')
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    # def update():
    #     b.rotation_z += 1
    #     b.rotation_y += 1
    #     b.rotation_x += 1
    # EditorCamera()

    app.run()
