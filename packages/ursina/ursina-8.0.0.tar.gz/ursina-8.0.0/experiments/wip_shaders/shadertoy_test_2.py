from panda3d.core import Shader


camera_contrast_shader = Shader.make('''

void vshader(float4 vtx_position : POSITION,
            float2 vtx_texcoord0 : TEXCOORD0,
            out float4 l_position : POSITION,
            out float2 l_texcoord0 : TEXCOORD0,
            uniform float4 texpad_tex,
            uniform float4x4 mat_modelproj)
{
    l_position=mul(mat_modelproj, vtx_position);
    l_texcoord0 = vtx_position.xz * texpad_tex.xy + texpad_tex.xy;
}

half3 AdjustContrast(half3 color, half contrast) {
    return saturate(lerp(half3(0.5, 0.5, 0.5), color, contrast));
}

void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform sampler2D k_tex : TEXUNIT0,
             uniform float2 iResolution,
             uniform float k_iTime)
{
    // o_color = float4(k_iTime,0,0,1);
    float2 uv = l_texcoord0/iResolution.xy;
    // float2 uv = l_texcoord0;
    float3 col = 0.5 + 0.5*cos(k_iTime+uv.xyx+float3(0,.4,.8));
    o_color = float4(col, 1.0);
}


''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    camera.shader = camera_contrast_shader
    camera.set_shader_input('iTime', 0)
    camera.set_shader_input('iResolution', (1,1))

    t = 0

    def update():
        global t
        t += time.dt
        camera.set_shader_input('iTime', t)

    EditorCamera()

    app.run()
