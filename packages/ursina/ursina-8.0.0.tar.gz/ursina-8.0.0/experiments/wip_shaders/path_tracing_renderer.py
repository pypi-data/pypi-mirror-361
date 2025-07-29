fragment_code = fragment='''
#version 130
 precision highp float;

 out vec4 fragColor;

 uniform vec3 eye;
 in vec3 initialRay;
 uniform float textureWeight;
 uniform float timeSinceStart;
 uniform sampler2D p3d_Texture0;
 uniform float glossiness;
 vec3 roomCubeMin = vec3(-4.99995, 0, -4.99995);
 vec3 roomCubeMax = vec3(4.99995, 9.9999, 4.99995);uniform vec3 light;
 uniform vec3 sphereCenter0;
 uniform float sphereRadius0;

 vec2 intersectCube(vec3 origin, vec3 ray, vec3 cubeMin, vec3 cubeMax) {
   vec3 tMin = (cubeMin - origin) / ray;
   vec3 tMax = (cubeMax - origin) / ray;
   vec3 t1 = min(tMin, tMax);
   vec3 t2 = max(tMin, tMax);
   float tNear = max(max(t1.x, t1.y), t1.z);
   float tFar = min(min(t2.x, t2.y), t2.z);
   return vec2(tNear, tFar);
 }

 vec3 normalForCube(vec3 hit, vec3 cubeMin, vec3 cubeMax) {
   if(hit.x < cubeMin.x + 0.0001) return vec3(-1.0, 0.0, 0.0);
   else if(hit.x > cubeMax.x - 0.0001) return vec3(1.0, 0.0, 0.0);
   else if(hit.y < cubeMin.y + 0.0001) return vec3(0.0, -1.0, 0.0);
   else if(hit.y > cubeMax.y - 0.0001) return vec3(0.0, 1.0, 0.0);
   else if(hit.z < cubeMin.z + 0.0001) return vec3(0.0, 0.0, -1.0);
   else return vec3(0.0, 0.0, 1.0);
 }

 float intersectSphere(vec3 origin, vec3 ray, vec3 sphereCenter, float sphereRadius) {
   vec3 toSphere = origin - sphereCenter;
   float a = dot(ray, ray);
   float b = 2.0 * dot(toSphere, ray);
   float c = dot(toSphere, toSphere) - sphereRadius*sphereRadius;
   float discriminant = b*b - 4.0*a*c;
   if(discriminant > 0.0) {
     float t = (-b - sqrt(discriminant)) / (2.0 * a);
     if(t > 0.0) return t;
   }
   return 10000.0;
 }

 vec3 normalForSphere(vec3 hit, vec3 sphereCenter, float sphereRadius) {
   return (hit - sphereCenter) / sphereRadius;
 }

 float random(vec3 scale, float seed) {
   return fract(sin(dot(gl_FragCoord.xyz + seed, scale)) * 43758.5453 + seed);
 }

 vec3 cosineWeightedDirection(float seed, vec3 normal) {
   float u = random(vec3(12.9898, 78.233, 151.7182), seed);
   float v = random(vec3(63.7264, 10.873, 623.6736), seed);
   float r = sqrt(u);
   float angle = 6.283185307179586 * v;
   vec3 sdir, tdir;
   if (abs(normal.x)<.5) {
     sdir = cross(normal, vec3(1,0,0));
   } else {
     sdir = cross(normal, vec3(0,1,0));
   }
   tdir = cross(normal, sdir);
   return r*cos(angle)*sdir + r*sin(angle)*tdir + sqrt(1.-u)*normal;
 }

 vec3 uniformlyRandomDirection(float seed) {
   float u = random(vec3(12.9898, 78.233, 151.7182), seed);
   float v = random(vec3(63.7264, 10.873, 623.6736), seed);
   float z = 1.0 - 2.0 * u;
   float r = sqrt(1.0 - z * z);
   float angle = 6.283185307179586 * v;
   return vec3(r * cos(angle), r * sin(angle), z);
 }

 vec3 uniformlyRandomVector(float seed) {
   return uniformlyRandomDirection(seed) * sqrt(random(vec3(36.7539, 50.3658, 306.2759), seed));
 }

 float shadow(vec3 origin, vec3 ray) {
   float tSphere0 = intersectSphere(origin, ray, sphereCenter0, sphereRadius0);
   if(tSphere0 < 1.0)
     return 0.0;
   return 1.0;
 }

vec3 calculateColor(vec3 origin, vec3 ray, vec3 light) {
    vec3 colorMask = vec3(1.0);
    vec3 accumulatedColor = vec3(0.0);
    for(int bounce = 0; bounce < 5; bounce++) {
        vec2 tRoom = intersectCube(origin, ray, roomCubeMin, roomCubeMax);
        float tSphere0 = intersectSphere(origin, ray, sphereCenter0, sphereRadius0);
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
            break;
        }
        else {
            if(false);

            else if(t == tSphere0)
                normal = normalForSphere(hit, sphereCenter0, sphereRadius0);

            ray = cosineWeightedDirection(timeSinceStart + float(bounce), normal);
        }
        vec3 toLight = light - hit;
        float diffuse = max(0.0, dot(normalize(toLight), normal));
        float shadowIntensity = shadow(hit + normal * 0.0001, toLight);
        colorMask *= surfaceColor;
        accumulatedColor += colorMask * (0.5 * diffuse * shadowIntensity);
        accumulatedColor += colorMask * specularHighlight * shadowIntensity;
        origin = hit;
    }
    return accumulatedColor;
}

 void main() {
   vec3 newLight = light + uniformlyRandomVector(timeSinceStart - 53.0) * 0.1;
   vec3 texture = texture2D(p3d_Texture0, gl_FragCoord.xy / vec2(512.0, 512)).rgb;
   fragColor = vec4(mix(calculateColor(eye, initialRay, newLight), texture, .5), 1.0);
   // fragColor = vec4(1,0,1, 1.0);
 }
'''
from panda3d.core import Shader

camera_contrast_shader = Shader.make(Shader.SL_GLSL,
vertex='''
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;

// attribute vec3 vertex;' +
uniform vec3 eye, ray00, ray01, ray10, ray11;
out vec3 initialRay;
void main() {
    vec2 percent = p3d_Vertex.xy * 0.5 + 0.5;
    initialRay = mix(mix(ray00, ray01, percent.y), mix(ray10, ray11, percent.y), percent.x);
    // gl_Position = p3d_Vertex;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    // texcoord = p3d_MultiTexCoord0;
}

// void main() {
//   gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
//   texcoord = p3d_MultiTexCoord0;
// }
''',

fragment=fragment_code, geometry='')


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='cube', color=color.orange)
    camera.shader = camera_contrast_shader
    # camera.set_shader_input('contrast', 1)

    eye = Vec3(0,0,0)

    t = 0

    mat = camera.lens.getProjectionMat()

    camera.set_shader_input('timeSinceStart', t)
    camera.set_shader_input('light', Vec3(0.4, 0.5, -0.6))
    camera.set_shader_input('eye', camera.position)
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
      t += time.dt * .5
      # t = t % 1
      # // print(t)
      # camera.set_shader_input('timeSinceStart', t)
      camera.set_shader_input('timeSinceStart', time.time())

      sampleCount += 1
      textureWeight = sampleCount / (sampleCount + 1)
      camera.set_shader_input('eye', camera.position)
      camera.set_shader_input('sampleCount', sampleCount)
      camera.set_shader_input('textureWeight', textureWeight)


    EditorCamera()

    app.run()
