from panda3d.core import Shader


camera_normals_shader = Shader.make('''

void vshader(float4 vtx_position : POSITION,
             out float4 l_position : POSITION,
             out float2 l_texcoord : TEXCOORD0,
             out float2 l_texcoordD : TEXCOORD1,
             out float2 l_texcoordN : TEXCOORD2,
             uniform float4 texpad_depth,
             uniform float4 texpad_normal,
             uniform float4x4 mat_modelproj)
{
  l_position = mul(mat_modelproj, vtx_position);
  l_texcoord = vtx_position.xz;
  l_texcoordD = (vtx_position.xz * texpad_depth.xy) + texpad_depth.xy;
  l_texcoordN = (vtx_position.xz * texpad_normal.xy) + texpad_normal.xy;
}


void fshader(out float4 o_color : COLOR,
             uniform float4 k_params1,
             uniform float4 k_params2,
             float2 l_texcoord : TEXCOORD0,
             float2 l_texcoordD : TEXCOORD1,
             float2 l_texcoordN : TEXCOORD2,
             uniform sampler2D k_random : TEXUNIT0,
             uniform sampler2D k_depth : TEXUNIT1,
             uniform sampler2D k_normal : TEXUNIT2)
{
    float4 c = tex2D(k_random, l_texcoord);
    o_color = c;
}

''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere')
    e = Entity(model='cube', y=-1)
    camera.shader = camera_normals_shader
    EditorCamera()

    app.run()
