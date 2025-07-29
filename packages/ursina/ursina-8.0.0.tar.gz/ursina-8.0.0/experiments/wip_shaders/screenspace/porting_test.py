from ursina import Shader; my_shader = Shader(fragment='''
#version 430

uniform sampler2D tex;
uniform sampler2D tex2;
in vec2 uv;
out vec4 color;
in vec2 window_size;

uniform bool on;
uniform float blur_size;
// #define img_size iResolution.xy

vec4 blur(sampler2D tex, vec2 uv, vec2 direction) {
    vec4 col = vec4(0.);

    for(float index=0; index<10; index++) {
        vec2 offset_uv = uv + vec2(
            (index/9 - 0.5) * blur_size * direction.x,
            (index/9 - 0.5) * blur_size * direction.y);
        col += texture(tex, offset_uv);
    }

    col = col / 10;
    texture(tex, uv);
    return col;
}

void main() {
    vec4 rgba = texture(tex, uv).rgba;
    vec4 vertical = blur(tex, uv, vec2(0.,1.));
    vec4 horizontal = blur(tex2, uv, vec2(1.,0.));

    color = (vertical*.5) + (horizontal*.5);

}

''',
default_input = dict(
    on = True,
    blur_size = .1
)
)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    buffer = base.win.makeTextureBuffer("My Buffer", *[int(e*1) for e in window.size])
    tex2 = buffer.getTexture()
    my_shader.default_input['tex2'] = tex2

    mycamera = base.makeCamera(buffer)
    mycamera.node().set_lens(camera.lens)
    mycamera.reparentTo(camera)


    e = Entity(model='sphere', color=color.yellow)
    e = Entity(model='cube', y=-1)
    camera.shader = my_shader

    settings = Empty(on=camera.shader.default_input['on'])

    def input(key):
        if key == 'space':
            settings.on = not settings.on
            camera.set_shader_input('on', settings.on)

        if key == '6':
            window.vsync = 60
        if key == '1':
            window.vsync = 100

    EditorCamera()
    window.vsync = 100

    app.run()
