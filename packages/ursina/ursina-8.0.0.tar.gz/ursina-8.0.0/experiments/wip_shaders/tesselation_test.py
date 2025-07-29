from ursina import *

tesselation_shader = Shader(language=Shader.GLSL,
vertex = '''
#version 400

in vec4 p3d_Vertex;
out vec3 controlpoint_wor;

void main() {
    controlpoint_wor = p3d_Vertex.xyz;
}
''',
tessControl='''

// Compute the tesselation factors here
layout(vertices = 3) out;
in vec3 controlpoint_wor[];
out vec3 tcPosition[];
uniform float TessLevelInner = 4.0;
uniform float TessLevelOuter = 4.0;

// #define ID gl_InvocationID

void main()
{
    tcPosition[ID] = controlpoint_wor[ID];
    if (ID == 0) {
        gl_TessLevelInner[0] = TessLevelInner;
        gl_TessLevelOuter[0] = TessLevelOuter;
        gl_TessLevelOuter[1] = TessLevelOuter;
        gl_TessLevelOuter[2] = TessLevelOuter;
    }
}
''',

tessEval='''
#version 400

// This shader creates the triangles
layout(triangles, equal_spacing, ccw) in;
in vec3 tcPosition[];
out vec3 tePosition;
out vec3 tePatchDistance;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    vec3 p0 = gl_TessCoord.x * tcPosition[0];
    vec3 p1 = gl_TessCoord.y * tcPosition[1];
    vec3 p2 = gl_TessCoord.z * tcPosition[2];
    tePatchDistance = gl_TessCoord;
    tePosition = (p0 + p1 + p2);
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(tePosition, 1);
}
// #endif
''',
fragment='''
// #ifdef _FRAGMENT_
// Final rendering (I know gl_FragColor is deprecated)
void main() {
    gl_FragColor = vec4(1,0,0,1);
}
// #endif

''',
default_input={
    'TessLevelInner' : 8.0,
    'TessLevelOuter' : 8.0,

}
)


if __name__ == '__main__':
    app = Ursina()
    window.color=color.black

    e = Entity(
        model=Circle(3),
        shader=tesselation_shader
    )

    # geomNode = e.model.geomNode
    # for i in range(geomNode.getNumGeoms()):
    #     geomNode.modifyGeom(i).makePatchesInPlace()

    # def input(key):
    #     if key == 'space':
    #         if not camera.shader:
    #             camera.shader = fxaa_shader
    #         else:
    #             camera.shader = None

    EditorCamera()
    app.run()
