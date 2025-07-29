from ursina import *; ssao_shader = Shader(fragment=''' #version 430
uniform sampler2D tex;
uniform sampler2D dtex;
uniform sampler2D ntex;
in vec2 uv;

uniform sampler2D noise_texture;
in flat int numsamples;
in float radius;
in float amount;
in float strength;
in float falloff;

uniform vec4 params1;
uniform vec4 params2;

out vec4 color;


vec3 sphere[16] = vec3[](
    vec3(0.53812504, 0.18565957, -0.43192).xyz,
    vec3(0.13790712, 0.24864247, 0.44301823).xyz,
    vec3(0.33715037, 0.56794053, -0.005789503).xyz,
    vec3(-0.6999805, -0.04511441, -0.0019965635).xyz,
    vec3(0.06896307, -0.15983082, -0.85477847).xyz,
    vec3(0.056099437, 0.006954967, -0.1843352).xyz,
    vec3(-0.014653638, 0.14027752, 0.0762037).xyz,
    vec3(0.010019933, -0.1924225, -0.034443386).xyz,
    vec3(-0.35775623, -0.5301969, -0.43581226).xyz,
    vec3(-0.3169221, 0.106360726, 0.015860917).xyz,
    vec3(0.010350345, -0.58698344, 0.0046293875).xyz,
    vec3(-0.08972908, -0.49408212, 0.3287904).xyz,
    vec3(0.7119986, -0.0154690035, -0.09183723).xyz,
    vec3(-0.053382345, 0.059675813, -0.5411899).xyz,
    vec3(0.035267662, -0.063188605, 0.54602677).xyz,
    vec3(-0.47761092, 0.2847911, -0.0271716).xyz
);


void main() {
    // vec3 rgb = normalize(texture(ntex, uv).rgb);
    //color.rgb = (1.-rgb)*10;

    float pixel_depth = texture(dtex, uv).a;
    vec3 pixel_normal = (texture(ntex, uv).xyz * 2.0 - 1.0);
    vec3 random_vector = normalize((texture(noise_texture, uv * 18.0 + pixel_depth + pixel_normal.xy).xyz * 2.0) - vec3(1.0)).xyz;
    float occlusion = 0.0;
    float radius = params1.z / pixel_depth;
    // float radius = radius / pixel_depth;
    float depth_difference;
    vec3 sample_normal;
    vec3 ray;
    // for(int i = 0; i < numsamples; ++i) {
    //     ray = radius * reflect(sphere[i], random_vector);
    //     sample_normal = (texture(ntex, uv + ray.xy).xyz * 2.0 - 1.0);
    //     depth_difference = (pixel_depth - texture(dtex, uv + ray.xy).r);
    //     // occlusion += step(params2.y, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(params2.y, params2.x, depth_difference));
    //     // occlusion += step(params2.y, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(params2.y, params2.x, depth_difference));
    //     occlusion += 100.;
    //     // occlusion += step(falloff, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(falloff, strength, depth_difference));
    // }
    ray = radius * reflect(sphere[0], random_vector);
    sample_normal = (texture(ntex, uv + ray.xy).xyz * 2.0 - 1.0);
    depth_difference = (pixel_depth - texture(dtex, uv + ray.xy).r);
    // occlusion += step(params2.y, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(params2.y, params2.x, depth_difference));
    occlusion += step(params2.y, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(params2.y, params2.x, depth_difference));
    occlusion *= 100.0;

    float amount = -amount / numsamples;
    color.rgb = texture(tex, uv).rgb + (occlusion * params1.y);
    // color.rgb = vec3(1.,1.,1.) + (occlusion * amount);
    // pixel_depth = (1.-pixel_depth) * 10;
    // color.rgb = vec3(1.,1.,1) * random_vector;
    // color.rgb = rgb;
    color.a = 1.;
}
// uniform mat4 p3d_ProjectionMatrixInverse;
// vec4 getViewPos(vec2 texCoord)
// {
// 	float x = texCoord.s * 2.0 - 1.0;
// 	float y = texCoord.t * 2.0 - 1.0;
// 	// Assume we have a normal depth range between 0.0 and 1.0
// 	float z = texture(ntex, texCoord).r * 2.0 - 1.0;
// 	vec4 posProj = vec4(x, y, z, 1.0);
// 	// vec4 posView = u_inverseProjectionMatrix * posProj;
// 	vec4 posView = p3d_ProjectionMatrixInverse * posProj;
//
// 	posView /= posView.w;
//
// 	return posView;
// }
// #define KERNEL_SIZE 16
//
// // uniform vec3 u_kernel[KERNEL_SIZE];
// uniform mat4 p3d_ProjectionMatrix;
// // uniform float u_radius;
//
// #define CAP_MIN_DISTANCE 0.0001 // This constant removes artifacts caused by neighbour fragments with minimal depth difference.
// #define CAP_MAX_DISTANCE 0.005 // This constant avoids the influence of fragments, which are too far away.
//
//
// void main() {
// 	vec4 posView = getViewPos(uv);
// 	vec3 normalView = normalize(texture(ntex, uv).xyz * 2.0 - 1.0);
// 	vec3 randomVector = normalize(texture(noise_texture, uv * 1.).xyz * 2.0 - 1.0);
// 	// vec3 randomVector = normalize(texture(noise_texture, v_texCoord * u_rotationNoiseScale).xyz * 2.0 - 1.0);
// 	vec3 tangentView = normalize(randomVector - dot(randomVector, normalView) * normalView);
// 	vec3 bitangentView = cross(normalView, tangentView);
// 	mat3 kernelMatrix = mat3(tangentView, bitangentView, normalView);
// 	// Go through the kernel samples and create occlusion factor.
// 	float occlusion = 0.0;
//
// 	for (int i = 0; i < KERNEL_SIZE; i++)
// 	{
// 		// vec3 sampleVectorView = kernelMatrix * u_kernel[i];
// 		vec3 sampleVectorView = kernelMatrix * sphere[i];
// 		vec4 samplePointView = posView + radius * vec4(sampleVectorView, 0.0);
// 		// vec4 samplePointNDC = u_projectionMatrix * samplePointView;
// 		vec4 samplePointNDC = p3d_ProjectionMatrix * samplePointView;
// 		samplePointNDC /= samplePointNDC.w;
// 		vec2 samplePointTexCoord = samplePointNDC.xy * 0.5 + 0.5;
// 		float zSceneNDC = texture(dtex, samplePointTexCoord).r * 2.0 - 1.0;
// 		float delta = samplePointNDC.z - zSceneNDC;
// 		// If scene fragment is before (smaller in z) sample point, increase occlusion.
// 		if (delta > CAP_MIN_DISTANCE && delta < CAP_MAX_DISTANCE)
// 		{
// 			occlusion += 1.0;
// 		}
// 	}
//
// 	// No occlusion gets white, full occlusion gets black.
// 	occlusion = 1.0 - occlusion / (float(KERNEL_SIZE) - 1.0);
//
// 	color = vec4(occlusion, occlusion, occlusion, 1.0);
//
// }
''',
default_input = dict(
    numsamples = 64,
    # -float(config.amount) / config.numsamples  #params1.y
    amount = 2.0,
    radius = 0.05,

    strength = 0.01,
    falloff = 0.000002,
)
)
app = Ursina()

camera.clip_plane_far = 100
camera.shader = ssao_shader
camera.set_shader_input('noise_texture', load_texture('noise')._texture)
camera.set_shader_input("params1", (64, -float(2.0) / 64, .05, 0))
camera.set_shader_input("params2", (.01, .000002, 0, 0))

base.render.setShaderAuto()


Entity(model='plane', scale=8)
Entity(model='cube', color=color.red, y=.5)
Entity(model='sphere', color=color.yellow, y=1, x=.75)

EditorCamera()
app.run()


# from direct.filter.CommonFilters import CommonFilters
# from direct.showbase.ShowBase import ShowBase
#
# app = ShowBase()
#
# m = loader.loadModel("panda.egg")
# m.reparentTo(render)
# # m.setY(20)
#
# filters = CommonFilters(base.win, base.cam)
# filters.setAmbientOcclusion(
#     numsamples=64,
#     # radius=0.05,
#     # amount=2.0,
#     # strength=0.01,
#     # falloff= 0.000002,
# )
#
# app.run()
