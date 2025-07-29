fragment_code = fragment='''
#version 130

out vec4 fragColor;
uniform sampler2D p3d_Texture0;
uniform int osg_FrameNumber;
in vec3 cam_pos;
in float textureWeight;
in vec3 initialRay;

float intersectSphere(vec3 origin, vec3 ray, vec3 center, float redius) {
    vec3 toSphere = origin - center;
    float a = dot(ray, ray);
    float b = 2.0 * dot(toSphere, ray);
    float c = dot(toSphere, toSphere) - redius*redius;
    float discriminant = b*b - 4.0*a*c;

    if(discriminant > 0.0) {
        float t = (-b - sqrt(discriminant)) / (2.0 * a);
        if(t > 0.0)
            return t;
        }
    return 10000.0;
}
float random(vec3 scale, float seed) {
  return fract(sin(dot(gl_FragCoord.xyz + seed, scale)) * 43758.5453 + seed);
}

vec3 calculateColor(vec3 origin, vec3 ray, vec3 light) {
    // if (random(vec3(.001,.1,.001), osg_FrameNumber) > 0.5) {
    //     return vec3(1,1,1);
    //
    // }
    vec3 colorMask = vec3(1.0);
    vec3 accumulatedColor = vec3(1,0,0);

    for(int bounce = 0; bounce < 5; bounce++) {
    // int bounce = 0;
    // vec2 tRoom = intersectCube(origin, ray, roomCubeMin, roomCubeMax);
        vec2 tRoom = vec2(0,0);
        float tSphere0 = intersectSphere(origin, ray, vec3(0,0,0), .25);
        vec3 surfaceColor = vec3(0.8, 0.8, 0.8);
        float t = 10000.0;

        if(tRoom.x < tRoom.y)
            t = tRoom.y;

        if(tSphere0 < t) {
            t = tSphere0;
            surfaceColor = vec3(0.0, 1.0, 0.1);
        }

        vec3 hit = origin + ray * t;

        float specularHighlight = 0.0;
        vec3 normal;

        if(t == tRoom.y) {
            normal = -normalForCube(hit, roomCubeMin, roomCubeMax);
            if(hit.x < -4.99895)
                surfaceColor = vec3(0.1, 0.1, 0.1);
            else if(hit.x > 4.99895)
                surfaceColor = vec3(0.1, 0.1, 0.1);
                ray = cosineWeightedDirection(timeSinceStart + float(bounce), normal);
        }

        else if(t == 10000.0) {
        if(t == 10000.0) {
            break;
        }
        else {
            if(false);

            // else if(t == tSphere0)
            //     normal = normalForSphere(hit, vec3(0,0,0), .25);

            // ray = cosineWeightedDirection(timeSinceStart + float(bounce), normal);
        }
    vec3 toLight = light - hit;
    float diffuse = max(0.0, dot(normalize(toLight), normal));
    // float shadowIntensity = shadow(hit + normal * 0.0001, toLight);
    colorMask *= surfaceColor;
    float shadowIntensity = 1;
    accumulatedColor += colorMask * (0.5 * diffuse * shadowIntensity);
    accumulatedColor += colorMask * specularHighlight * shadowIntensity;
    origin = hit;
    }
    return accumulatedColor;
}

void main() {
    fragColor = vec4(0,1,0,1);
    vec3 texture = texture2D(p3d_Texture0, gl_FragCoord.xy / vec2(1920, 1080)).rgb;

    vec3 newLight = vec3(1,1,1); //temp
    // int textureWeight = 1;

    fragColor = vec4(mix(calculateColor(cam_pos, initialRay, newLight), texture, textureWeight), 1.0);
}
'''









from panda3d.core import Shader

camera_contrast_shader = Shader.make(Shader.SL_GLSL,
vertex='''
#version 130


uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
// in vec2 p3d_MultiTexCoord0;
// out vec2 texcoord;
uniform vec3 cam_pos, ray00, ray01, ray10, ray11;
out vec3 initialRay;

void main() {
    vec2 percent = p3d_Vertex.xy * 0.5 + 0.5;
    initialRay = mix(mix(ray00, ray01, percent.y), mix(ray10, ray11, percent.y), percent.x);
    // gl_Position = p3d_Vertex;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    // texcoord = p3d_MultiTexCoord0;
}
''',

fragment=fragment_code, geometry='')


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='cube', color=color.orange)
    camera.shader = camera_contrast_shader
    # camera.set_shader_input('contrast', 1)

    cam_pos = Vec3(0,0,0)

    t = 0

    mat = camera.lens.getProjectionMat()

    camera.set_shader_input('cam_pos', cam_pos)
    # camera.set_shader_input('light', Vec3(0.4, 0.5, -0.6))
    camera.set_shader_input('ray00', mat[0][0])
    camera.set_shader_input('ray01', mat[0][1])
    camera.set_shader_input('ray10', mat[1][0])
    camera.set_shader_input('ray11', mat[1][1])

    camera.set_shader_input('sphereCenter0', Vec3(0,1,1))
    camera.set_shader_input('sphereRadius0', .25)

    sampleCount = 0
    textureWeight = sampleCount / (sampleCount + 1)

    def update():
      global t, sampleCount
      t += 1
      #t += time.dt * .5
      #t = t % 1
      # // print(t)

      sampleCount += 1
      textureWeight = sampleCount / (sampleCount + 1)
      camera.set_shader_input('sampleCount', sampleCount)
      camera.set_shader_input('textureWeight', textureWeight)


    EditorCamera()
    window.size *= .5
    window.position += Vec2(900, -100)

    app.run()
