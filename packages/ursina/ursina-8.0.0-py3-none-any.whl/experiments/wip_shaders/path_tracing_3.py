from panda3d.core import Shader


shader_code = '''

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

void vshader(float4 vtx_position : POSITION,
            float2 vtx_texcoord0 : TEXCOORD0,
            out float4 l_position : POSITION,
            out float2 l_texcoord0 : TEXCOORD0,
            uniform float4 texpad_tex,
            uniform float4x4 mat_modelproj)
{
    l_position=mul(mat_modelproj, vtx_position);
    l_texcoord0 = vtx_position.xy * texpad_tex.xy + texpad_tex.xy;
}

half3 AdjustContrast(half3 color, half contrast) {
    return saturate(lerp(half3(0.5, 0.5, 0.5), color, contrast));
}
float hash( const float n ) {
	return fract(sin(n)*43758.54554213);
}
float2 hash2( const float n ) {
	return fract(sin(float2(n,n+1.))*float2(43758.5453123));
}
float2 hash2( const float2 n ) {
	return fract(sin(float2( n.x*n.y, n.x+n.y))*float2(25.1459123,312.3490423));
}
float3 hash3( const float2 n ) {
	return fract(sin(float3(n.x, n.y, n+2.0))*float3(36.5453123,43.1459123,11234.3490423));
}

float intersectPlane( const float3 cam_pos, const float3 rd, const float height) {
	if (rd.y==0.0) return 500.;
	float d = -(cam_pos.y - height)/rd.y;
	if( d > 0. ) {
		return d;
	}
	return 500.;
}

float intersectUnitSphere ( const float3 cam_pos, const float3 rd, const float radius, const float3 sph ) {
	float3  ds = cam_pos - sph;
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


//
// Scene
//

// void getSphereOffset( const float2 grid, out float2 center ) {
// 	center = (hash2( grid+float2(43.12,1.23) ) - float2(0.5) )*(GRIDSIZESMALL);
//     center = 0;
// }
// void getSpherePosition( const float2 grid, const float2 sphereOffset, out float3 center ) {
// 	float2 offset = grid + sphereOffset;
// 	center = float3( offset.x, 0., offset.y ) + 0.5*float3( GRIDSIZE, 2., GRIDSIZE );
// }
// float3 getSphereColor( const float2 grid ) {
// 	//float3 col = hash3( grid+float2(43.12*grid.y,12.23*grid.x) );
//     float3 col = (1,1,1);
//     return mix(col,col*col,.8);
// }

float3 getBackgroundColor( const float3 cam_pos, const float3 rd ) {
	return 1.4*mix(float3(.5),float3(.6,.8,.9), .5+.5*rd.y);
}

float3 trace(const float3 cam_pos, const float3 rd, out float3 intersection, out float3 normal,
           out float dist, out int material, const int steps,
           TRACE_FUNC_INPUT
       ) {
	dist = MAXDISTANCE;
	float distcheck;

	float3 col, normalcheck;

	material = 0;
	col = getBackgroundColor(cam_pos, rd);

    // ground plane
	if( (distcheck = intersectPlane( cam_pos,  rd, 0.)) < MAXDISTANCE ) {
		dist = distcheck;
		material = 1;
		normal = float3(0, 1, 0);
		col = float3(.2, .5, .05);
	}

	// trace grid

	float3 pos = cam_pos;
	float3 ri = 1.0/rd;
	float3 rs = sign(rd);
	float3 dis = (pos-cam_pos + 0.5  + rs*0.5) * ri;
	float3 mm = float3(0.0);
	float2 offset;

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

float2 rv2;

float3 cosWeightedRandomHemisphereDirection2( const float3 n ) {
	float3  uu = normalize( cross( n, float3(0.0,1.0,1.0) ) );
	float3  vv = cross( uu, n );

	float ra = sqrt(rv2.y);
	float rx = ra*cos(6.2831*rv2.x);
	float ry = ra*sin(6.2831*rv2.x);
	float rz = sqrt( 1.0-rv2.y );
	float3  rr = float3( rx*uu + ry*vv + rz*n );

    return normalize( rr );
}

void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform sampler2D k_tex : TEXUNIT0,
             uniform float2 iResolution,
             uniform float k_iTime,
	           uniform float k_iFrame,
             uniform float3 k_camera_rotation,
             uniform float3 k_camera_forward,
             uniform float3 k_camera_position,
             FSHADER_INPUT
             // uniform float3 k_sphere_0_position,
             // uniform float3 k_sphere_1_position,
             // uniform float k_sphere_0_radius,
             // uniform float k_sphere_1_radius
         )
{
    float2 uv = l_texcoord0/iResolution.xy;
    // float2 uv = l_texcoord0;
    // float3 col = 0.5 + 0.5*cos(k_iTime+uv.xyx+float3(0,.4,.8));

    time = k_iTime;
        // float2 q = fragCoord.xy/iResolution.xy;
    float2 q = l_texcoord0.xy;
  	float2 p = -1.0+2.0*q;
  	p.x *= iResolution.x/iResolution.y;

  	float3 col = float3( 0. );

  	// raytrace
  	int material;
  	float3 normal, intersection;
  	float dist;
  	float seed = time+(p.x+iResolution.x*p.y)*1.51269341231;

  	for( int j=0; j<SAMPLES + min(0,k_iFrame); j++ ) {
  		float fj = float(j);


  		rv2 = hash2( 24.4316544311*fj+time+seed );

  		float2 pt = p+rv2/(0.5*iResolution.xy);

  		// camera
  		// float3 cam_pos = float3( cos( 0.232*time) * 10., 6.+3.*cos(0.3*time), GRIDSIZE*(time/SPEED) );
  		// float3 look_dir = cam_pos + float3( -sin( 0.232*time) * 10., -2.0+cos(0.23*time), 10.0 );
  		float3 cam_pos = k_camera_position; // position
  		float3 look_dir = cam_pos + k_camera_forward;

        // look_dir = float3(k_camera_rotation.y, -2.0+cos(0.23), 10)
  		// float roll = -0.15*sin(0.5*time);
        float roll = 0;
  		// camera tx
  		float3 cw = normalize( look_dir-cam_pos );
  		float3 cp = float3( sin(roll), cos(roll), 0.0 );
  		float3 cu = normalize( cross(cw,cp) );
  		float3 cv = normalize( cross(cu,cw) );

  		float3 rd = normalize( pt.x*cu + pt.y*cv + 1.5*cw );

  		float3 colsample = float3( 1. );

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
                        // k_sphere_0_position, k_sphere_0_radius,
                        // k_sphere_1_position, k_sphere_1_radius
                    );
  			}
  		}
  		colsample = sqrt(clamp(colsample, 0., 1.));
  		if( material == 0 ) {
  			col += colsample;
  		}
  	}
  	col  /= float(SAMPLES);




    o_color = float4(col, 1.0);
}


'''



if __name__ == '__main__':
    from ursina import *
    from PIL import Image
    # from panda3d.core import Texture as PandaTexture
    window.vsync = False
    app = Ursina()

    class Player(Entity):
        def __init__(self, **kwargs):
            super().__init__(model='sphere', color=color.red, **kwargs)
            self.speed = 10

        def update(self):
            h = max((held_keys['gamepad left stick x'], held_keys['d']-held_keys['a']), key=lambda x: abs(x))
            v = max((held_keys['gamepad left stick y'], held_keys['w']-held_keys['s']), key=lambda x: abs(x))
            self.direction = Vec3(h,0,v).normalized()
            self.input_strength = min(Vec3(h,0,v).length(), 1)
            self.velocity = self.direction * time.dt * self.speed * self.input_strength
            self.position += self.velocity

    Player()

    quad = Entity(model='quad', texture=Texture(Image.new(mode="RGBA", size=(1920//8,1080//8))), scale=(16,9), always_on_top=True)
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

    trace_func_input = '\n'.join([f'const float3 sphere_{i}_position, const float sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]
    fshader_input = '\n'.join([f'uniform float3 k_sphere_{i}_position, uniform float k_sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]
    trace_call_code = '\n'.join([f'k_sphere_{i}_position, k_sphere_{i}_radius, ' for i in range(len(spheres))])[:-2]

    distcheck_code = ''
    for i, sphere in enumerate(spheres):
        distcheck_code += f'''
        if( (distcheck = intersectUnitSphere( cam_pos, rd, sphere_{i}_radius, sphere_{i}_position )) < dist ) {{
            dist = distcheck;
            normal = normalize((cam_pos+rd*dist)-sphere_{i}_position);
            col = float3({sphere.color.r},{sphere.color.g},{sphere.color.b});
            material = 2;
        }}'''



    # print('----------', fshader_input)
    shader_code = shader_code.replace('TRACE_FUNC_INPUT', trace_func_input)
    shader_code = shader_code.replace('DISTCHECK_CODE', distcheck_code)
    shader_code = shader_code.replace('FSHADER_INPUT', fshader_input)
    shader_code = shader_code.replace('TRACE_CALL_CODE', trace_call_code)
    # for i, l in enumerate(shader_code.split('\n')):
    #     print(i, l)
    from panda3d.core import Shader
    camera_contrast_shader = Shader.make(shader_code, Shader.SL_Cg)
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
    window.size = (400,300)
    app.run()
