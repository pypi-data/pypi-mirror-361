from ursina import *

sky_shader = Shader(
    vertex='''
#version 330 core

// Inputs
in vec3 position;
in vec2 uv;

// Outputs
out vec2 vUv;
out vec3 vPosition;

void main() {
    vUv = uv;
    vPosition = position;
    gl_Position = vec4(position, 1.0);
}
''',
fragment='''
#version 330 core

// Inputs from the vertex shader
in vec2 vUv;
in vec3 vPosition;

// Output color
out vec4 FragColor;

// Uniforms
uniform vec3 sunDirection;  // Direction of the sun
uniform vec3 cloudColor;    // Base color of the clouds
uniform float cloudDensity; // Density factor
uniform float time;         // Time for animation

// 3D noise function for cloud density
float hash(vec3 p) {
    return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453123);
}

float noise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    vec3 u = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(
            mix(hash(i + vec3(0.0, 0.0, 0.0)), hash(i + vec3(1.0, 0.0, 0.0)), u.x),
            mix(hash(i + vec3(0.0, 1.0, 0.0)), hash(i + vec3(1.0, 1.0, 0.0)), u.x),
            u.y),
        mix(
            mix(hash(i + vec3(0.0, 0.0, 1.0)), hash(i + vec3(1.0, 0.0, 1.0)), u.x),
            mix(hash(i + vec3(0.0, 1.0, 1.0)), hash(i + vec3(1.0, 1.0, 1.0)), u.x),
            u.y),
        u.z);
}

float fbm(vec3 p) {
    float value = 0.0;
    float scale = 1.0;
    float weight = 0.5;

    for (int i = 0; i < 5; i++) {
        value += weight * noise(p * scale);
        scale *= 2.0;
        weight *= 0.5;
    }

    return value;
}

// Raymarching through the 3D volume
vec4 raymarchClouds(vec3 ro, vec3 rd) {
    float t = 0.0;
    float density = 0.0;
    vec3 accumulatedColor = vec3(0.0);

    for (int i = 0; i < 64; i++) {
        vec3 p = ro + rd * t; // Sample point along the ray
        float d = fbm(p + vec3(time * 0.05)); // Get density from 3D noise
        density += d * 0.1; // Accumulate density
        accumulatedColor += d * cloudColor; // Accumulate color
        t += 0.1; // Increment ray step
        if (density > 1.0) break; // Exit early if density is too high
    }

    // Blend clouds with background sky (simple blending for now)
    return vec4(accumulatedColor / 64.0, density);
}

void main() {
    vec3 ro = vec3(vPosition.xy, 0.0); // Ray origin (camera position)
    vec3 rd = normalize(vec3(vUv - 0.5, 1.0)); // Ray direction

    vec4 clouds = raymarchClouds(ro, rd);
    FragColor = clouds;
}


''',
default_input={
    "sunDirection": (0.5, 0.5, -1),  # Normalized direction of the sun
    "horizonColor": color.blue,  # Sky near the horizon
    "zenithColor": color.pink,   # Sky at the zenith (overhead)
    "cloudColor": (1.0, 1.0, 1.0),    # Base color of clouds
    "cloudDensity": 0.8,              # Adjusts cloud density (0 = none, 1 = thick clouds)
    "time": 0                         # Starting time for animation
}
)


if __name__ == '__main__':
    app = Ursina()
    sky = Sky(
        # model="sphere",
        # scale=500,
        # rotation=(90, 0, 0),
        # double_sided=True,
        shader=sky_shader,
        t=0,
        # ignore=True
    )
    EditorCamera()
    Entity(model='cube')

    def update():
        sky.t += time.dt
        sky.set_shader_input('time', sky.t)

    app.run()
