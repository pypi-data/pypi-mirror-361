from ursina import *

app = Ursina()
from ursina.shaders import lit_with_shadows_shader
Entity.default_shader = lit_with_shadows_shader

player = Entity(model='wireframe_cube', origin_y=-.5, color=color.red)
player.graphics_parent = Entity(model='cube')
rotation_smoother = Entity()
player.graphics = Entity(parent=rotation_smoother, model='ambulance', rotation_y=180)

# Entity(parent=player.graphics, model='cube', scale=(1,.05,.05), color=color.magenta, origin_x=-.5)

# rotation_helper = Entity(model='wireframe_cube', scale=(.05,1,.05), color=color.green, always_on_top=True, origin_y=-.5)

random.seed(0)
height_values = [[random.randint(0,64) for x in range(16)] for y in range(16)]

terrain_entity = Entity(model=Terrain(height_values=height_values), scale=Vec3(64,16,64), texture='grass', collider='mesh')
ec = EditorCamera()

def update():
    player.rotation_y += (held_keys['d'] - held_keys['a']) * time.dt * 100
    player.position += player.forward * Vec3(1,0,1) * (held_keys['w'] - held_keys['s']) * time.dt * 8

    # y, normal = terraincast(player.position, terrain, height_values, return_normals=True)
    y, normal = terraincast(player.world_position, terrain_entity, height_values, return_normals=True)
    print(y)
    player.y = y
    player.graphics_parent.look_at(player.position + normal, Vec3.up,)
    temp = player.rotation_y
    player.graphics_parent.position = player.position
    # player.graphics_parent.look_at(normal, 'forward', normal)

    # player.graphics_parent.rotate((0, temp, 0))
    # rotation_smoother.position = player.position
    # rotation_smoother.quaternion = slerp(rotation_smoother.quaternion, player.graphics_parent.quaternion, time.dt*5)
    # rotation_smoother.quaternion = player.graphics_parent.quaternion

sun = DirectionalLight()
sun.look_at(Vec3(1,-1,1))
Sky()
ec.target_z = -30
app.run()
