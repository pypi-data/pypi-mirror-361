from ursina import *


curl_shader = Shader(
fragment='''
#version 430

uniform sampler2D tex;
in vec2 uv;
in vec2 window_size;
#define aspect_ratio 1.7777
uniform vec2 velocity;
out vec4 gl_FragColor;
#define vL vec2(0., 0.);
#define vR vec2(1., 0.);
#define vT vec2(1., 0.);

void main() {
    float L = texture2D(tex, vL).y;
    float R = texture2D(tex, vR).y;
    float T = texture2D(tex, vT).x;
    float B = texture2D(tex, vB).x;
    float vorticity = R - L - T + B;
    gl_FragColor = vec4(0.5 * vorticity, 0.0, 0.0, 1.0);
}
''',
default_input=dict(
    blur_size = .1,
    velocity = Vec2(0,0),
    texel_size = Vec2(1/512, 1/512)
))

if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16

    # manager = FilterManager(base.win, base.cam)
    # tex1 = Texture()
    # tex2 = Texture()
    # finalquad = manager.renderSceneInto(colortex=tex1)
    # interquad = manager.renderQuadInto(colortex=tex2)
    # interquad.setShader(Shader.load("stage1.sha"))
    # interquad.setShaderInput("tex1", tex1)
    # finalquad.setShader(Shader.load("stage2.sha"))
    # finalquad.setShaderInput("tex2", tex2)


    camera.shader = curl_shader

    # // self.renderBufferTexture = Texture()

    def multipleSplats(amount):
        for i in range(amount):
            c = color.random_color() * 10
            x = random.random()
            y = random.random()
            dx = 1000 * (random.random() - 0.5)
            dy = 1000 * (random.random() - 0.5)
            splat(x, y, dx, dy, c)

    def splat (x, y, dx, dy, color):
    #     // splatProgram.bind();
        # gl.uniform1i(splatProgram.uniforms.uTarget, velocity.read.attach(0));
        camera.set_shader_input('aspectRatio', 16/9)
        camera.set_shader_input('point', Vec2(x, y))
    #     gl.uniform3f(splatProgram.uniforms.color, dx, dy, 0.0);
        camera.set_shader_input('color', Vec3(dx, dy, 0))
    #     gl.uniform1f(splatProgram.uniforms.radius, correctRadius(config.SPLAT_RADIUS / 100.0));
        camera.set_shader_input('radius', .25 / 100)
    #     blit(velocity.write);
    #     velocity.swap();
    #
    #     gl.uniform1i(splatProgram.uniforms.uTarget, dye.read.attach(0));
    #     gl.uniform3f(splatProgram.uniforms.color, color.r, color.g, color.b);
    #     blit(dye.write);
    #     dye.swap();
    # }

    multipleSplats(int(random.random() * 20) + 5)

    app.run()
