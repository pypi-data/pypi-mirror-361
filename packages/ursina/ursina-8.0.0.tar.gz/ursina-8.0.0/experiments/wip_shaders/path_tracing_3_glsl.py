from panda3d.core import Shader


vertex = '''
#define SAMPLES 8
#define PATHDEPTH 2

#define RAYCASTSTEPS 1
#define RAYCASTSTEPSRECURSIVE 2

#define EPSILON 0.001
#define MAXDISTANCE 180. //180
#define MAXHEIGHT 30.
#define SPEED 1.0
float time;
vec3 normal;

#version 420
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 fragCoord;
out vec3 position;
out vec2 texcoord0;

void main() {
{
    position=mul(mat_modelproj, p3d_Vertex);
    //texcoord0 = p3d_Vertex.xz * texpad_tex.xy + texpad_tex.xy;
    texcoord0 = p3d_Vertex.xz;
}

vec3 AdjustContrast(vec3 color, float contrast) {
    return saturate(lerp(vec3(0.5, 0.5, 0.5), color, contrast));
}
float hash( const float n ) {
	return fract(sin(n)*43758.54554213);
}
vec2 hash2( const float n ) {
	return fract(sin(vec2(n,n+1.))*vec2(43758.5453123));
}
vec2 hash2( const vec2 n ) {
	return fract(sin(vec2( n.x*n.y, n.x+n.y))*vec2(25.1459123,312.3490423));
}
vec3 hash3( const vec2 n ) {
	return fract(sin(vec3(n.x, n.y, n+2.0))*vec3(36.5453123,43.1459123,11234.3490423));
}

float intersectPlane( const vec3 cam_pos, const vec3 rd, const float height) {
	if (rd.y==0.0) return 500.;
	float d = -(cam_pos.y - height)/rd.y;
	if( d > 0. ) {
		return d;
	}
	return 500.;
}

float intersectUnitSphere ( const vec3 cam_pos, const vec3 rd, const float radius, const vec3 sph ) {
	vec3  ds = cam_pos - sph;
	float b = dot( rd, ds );
	float cs = dot( ds, ds ) - (radius*radius);
	float discriminant = b*b - cs;

	if( discriminant > 0.0 ) {
		float t = -b - sqrt( discriminant );
        // float t = (-b - sqrt(discriminant)) / (2.0 * a);
		if( t > 0. ) {
			return t;
		}
	}
	return 500.;
}


vec3 getBackgroundColor( const vec3 cam_pos, const vec3 rd ) {
	return 1.4*mix(vec3(.5),vec3(.6,.8,.9), .5+.5*rd.y);
}

vec3 trace(const vec3 cam_pos, const vec3 rd, out vec3 intersection, out vec3 normal,
           out float dist, out int material, const int steps,
           TRACE_FUNC_INPUT
       ) {
	dist = MAXDISTANCE;
	float distcheck;

	vec3 col, normalcheck;

	material = 0;
	col = getBackgroundColor(cam_pos, rd);

    // ground plane
	if( (distcheck = intersectPlane( cam_pos,  rd, 0.)) < MAXDISTANCE ) {
		dist = distcheck;
		material = 1;
		normal = vec3(0, 1, 0);
		col = vec3(.2, .5, .05);
	}

	// trace grid

	vec3 pos = cam_pos;
	vec3 ri = 1.0/rd;
	vec3 rs = sign(rd);
	vec3 dis = (pos-cam_pos + 0.5  + rs*0.5) * ri;
	vec3 mm = vec3(0.0);
	vec2 offset;

    float radius = 4;

	for( int i=0; i<steps; i++ )	{
		if( material == 2 || distance( cam_pos.xz, pos.xz ) > dist ) break; {
            DISTCHECK_CODE


			// mm = step(dis.xyz, dis.zyx);
			// dis += mm * rs * ri;
			// pos += mm * rs;
		}
	}

	intersection = cam_pos+rd*dist;

	return col;
}

vec2 rv2;

vec3 cosWeightedRandomHemisphereDirection2( const vec3 n ) {
	vec3  uu = normalize( cross( n, vec3(0.0,1.0,1.0) ) );
	vec3  vv = cross( uu, n );

	float ra = sqrt(rv2.y);
	float rx = ra*cos(6.2831*rv2.x);
	float ry = ra*sin(6.2831*rv2.x);
	float rz = sqrt( 1.0-rv2.y );
	vec3  rr = vec3( rx*uu + ry*vv + rz*n );

    return normalize( rr );
}
'''

fragment = '''
in vec2 texcoord0;
out vec4 o_color;
uniform sampler2D tex;
uniform vec2 iResolution;
uniform float iTime;
uniform float iFrame;
uniform vec3 k_camera_rotation,
uniform vec3 k_camera_forward,
uniform vec3 k_camera_position,
FSHADER_INPUT

void main()
{
    vec2 uv = texcoord0/iResolution.xy;
    // vec2 uv = texcoord0;
    // vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,.4,.8));

    time = iTime;
        // vec2 q = fragCoord.xy/iResolution.xy;
    vec2 q = texcoord0.xy;
  	vec2 p = -1.0+2.0*q;
  	p.x *= iResolution.x/iResolution.y;

  	vec3 col = vec3( 0. );

  	// raytrace
  	int material;
  	vec3 normal, intersection;
  	float dist;
  	float seed = time+(p.x+iResolution.x*p.y)*1.51269341231;

  	for( int j=0; j<SAMPLES + min(0,k_iFrame); j++ ) {
  		float fj = float(j);


  		rv2 = hash2( 24.4316544311*fj+time+seed );

  		vec2 pt = p+rv2/(0.5*iResolution.xy);

  		// camera
  		// vec3 cam_pos = vec3( cos( 0.232*time) * 10., 6.+3.*cos(0.3*time), GRIDSIZE*(time/SPEED) );
  		// vec3 look_dir = cam_pos + vec3( -sin( 0.232*time) * 10., -2.0+cos(0.23*time), 10.0 );
  		vec3 cam_pos = camera_position; // position
  		vec3 look_dir = cam_pos + camera_forward;

        // look_dir = vec3(camera_rotation.y, -2.0+cos(0.23), 10)
  		// float roll = -0.15*sin(0.5*time);
        float roll = 0;
  		// camera tx
  		vec3 cw = normalize( look_dir-cam_pos );
  		vec3 cp = vec3( sin(roll), cos(roll), 0.0 );
  		vec3 cu = normalize( cross(cw,cp) );
  		vec3 cv = normalize( cross(cu,cw) );

  		vec3 rd = normalize( pt.x*cu + pt.y*cv + 1.5*cw );

  		vec3 colsample = vec3( 1. );

  		// first hit
  		rv2 = hash2( (rv2.x*2.4543263+rv2.y)*(time+1.) );
  		colsample *= trace(cam_pos, rd, intersection, normal, dist, material, RAYCASTSTEPS,
                TRACE_CALL_CODE
            );

  		// bounces
  		for( int i=0; i<(PATHDEPTH-1); i++ ) {
  			if( material != 0 ) {
  				rd = cosWeightedRandomHemisphereDirection2( normal );
  				cam_pos = intersection + EPSILON*rd;

  				rv2 = hash2( (rv2.x*2.4543263+rv2.y)*(time+1.)+(float(i+1)*.23) );

  				colsample *= trace(cam_pos, rd, intersection, normal, dist, material, RAYCASTSTEPSRECURSIVE,
                    TRACE_CALL_CODE
                        // sphere_0_position, k_sphere_0_radius,
                        // sphere_1_position, k_sphere_1_radius
                    );
  			}
  		}
  		colsample = sqrt(clamp(colsample, 0., 1.));
  		if( material == 0 ) {
  			col += colsample;
  		}
  	}
  	col  /= float(SAMPLES);




    o_color = vec4(col, 1.0);
}


'''



if __name__ == '__main__':
    from ursina import *
    from PIL import Image
    # from panda3d.core import Texture as PandaTexture
    window.vsync = False
    app = Ursina()

    quad = Entity(model='quad', texture=Texture(Image.new(mode="RGBA", size=(1920//2,1080//2))), scale=(16,9), always_on_top=True)
    quad.world_parent=camera
    # quad = Entity(parent=camera.ui, model='quad', texture=Texture(Image.new(mode="RGBA", size=(1920,1080))), scale=(camera.aspect_ratio, 1))
    quad.texture.filtering = None

    camera.position = (0,0,0)
    camera_rotation = [0,0,0]
    dummy_object = camera
    direction = Entity(parent=dummy_object, z=1)
    t = 0
    frame = 0

    random.seed(0)
    spheres = list()
    for z in range(3):
        for y in range(3):
            for x in range(3):
                Entity(model='sphere', position=(x*5,y*5,z*5), color=color.random_color(), scale=random.uniform(.1,10))

    spheres = [e for e in scene.entities if e.model and e.model.name == 'sphere']
    # for e in scene.entities:
    #     if e.model:
    #         print(e.name, e.model.name)

    trace_func_input = '\n'.join([f'const vec3 sphere_{i}_position, const float sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]
    fshader_input = '\n'.join([f'uniform vec3 k_sphere_{i}_position, uniform float k_sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]
    trace_call_code = '\n'.join([f'k_sphere_{i}_position, k_sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]

    distcheck_code = ''
    for i, sphere in enumerate(spheres):
        distcheck_code += f'''
        if( (distcheck = intersectUnitSphere( cam_pos, rd, sphere_{i}_radius, sphere_{i}_position )) < dist ) {{
            dist = distcheck;
            normal = normalize((cam_pos+rd*dist)-sphere_{i}_position);
            col = vec3({sphere.color.r},{sphere.color.g},{sphere.color.b});
            material = 2;
        }}'''



    # print('----------', fshader_input)
    vertex = vertex.replace('TRACE_FUNC_INPUT', trace_func_input)
    vertex = vertex.replace('DISTCHECK_CODE', distcheck_code)
    fragment = fragment.replace('FSHADER_INPUT', fshader_input)
    fragment = fragment.replace('TRACE_CALL_CODE', trace_call_code)
    # for i, l in enumerate(shader_code.split('\n')):
    #     print(i, l)
    camera_contrast_shader = Shader(vertex=vertex, fragment=fragment, gometry='')
    quad.shader = camera_contrast_shader
    quad.set_shader_input('iTime', 0)
    quad.set_shader_input('iFrame', 0)
    # quad.set_shader_input('iResolution', window.size / 2)
    quad.set_shader_input('iResolution', quad.texture.size)
    quad.set_shader_input('tex', quad.texture._texture)
    quad.set_shader_input('camera_rotation', camera.position)
    quad.set_shader_input('camera_forward', camera.right)
    quad.set_shader_input('camera_position', (0,0,0))

    for i, e in enumerate(spheres):
        # print(i, e.model.name)
        quad.set_shader_input(f'sphere_{i}_position', (-e.world_x*2, e.world_y*2, e.world_z*2))
        quad.set_shader_input(f'sphere_{i}_radius', e.world_scale[0])


    def update():
        global t, frame, camera_rotation, spheres
        t += time.dt

        quad.set_shader_input('iTime', t)
        quad.set_shader_input('iFrame', frame)
        dir = direction.world_position-dummy_object.world_position
        dir[0] *= -1
        quad.set_shader_input('camera_forward', dir)
        quad.set_shader_input('camera_position', (-dummy_object.world_x, dummy_object.world_y, dummy_object.world_z))

        for i, e in enumerate(spheres):
            quad.set_shader_input(f'sphere_{i}_position', (-e.world_x*2, e.world_y*2, e.world_z*2))
            quad.set_shader_input(f'sphere_{i}_radius', e.world_scale[0])



    def input(key):
        if key == 'tab':
            quad.enabled = not quad.enabled


    camera.position=(0,1,-10)
    EditorCamera()
    window.fps_counter.color = color.black
    # window.size /= 2
    app.run()
