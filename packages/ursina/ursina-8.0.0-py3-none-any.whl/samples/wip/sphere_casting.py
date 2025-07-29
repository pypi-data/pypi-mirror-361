from ursina import *

def length(v):
    return sqrt(v.x*v.x + v.y*v.y)

def signed_distance_to_circle(point, center, radius):
    return length(center-point) - radius


app = Ursina()

random.seed(1)
camera.orthographic = True
camera.fov = 1
window.color = color.black
bg = Entity(model='quad', scale=(window.aspect_ratio, 1) * 1000, collider='box', color=color._32, visible=False)
origin = Entity()
origin_renderer = Entity(parent=origin, model='sphere', color=color.yellow, scale=.025)
line = Entity(parent=origin, model='cube', origin_z=-.5, scale=(.0025, .0025, 999), color=color.gray)
current_point = Entity(parent=origin, model='sphere', color=color.white33)
world_space_cursor = Entity(model='circle', color=color.pink, scale=.0125, always_on_top=True)
mouse.visible = False

objects = list()
for i in range(8):
    objects.append(Entity(model='circle', scale=random.uniform(.05, .3), x=random.random()-.5, y=random.random()-.5, color=color.gray))


sphere_renderers = [Entity(model='circle', color=color.color(180,1,1,.25), enabled=False) for i in range(100)]


def update():
    world_space_cursor.position = mouse.world_point
    origin.look_at(world_space_cursor)
    origin.x += (held_keys['d'] - held_keys['a']) * time.dt * .25
    origin.y += (held_keys['w'] - held_keys['s']) * time.dt * .25



def input(key):
    if key == 'left mouse down':
        # reset
        current_point.position = (0, 0, 0)
        for sphere in sphere_renderers:
            sphere.enabled = False

        # sphere cast
        for i, sphere in enumerate(sphere_renderers):
            distances = [signed_distance_to_circle(current_point.world_position, e.world_position, e.scale_x/2) for e in objects]
            new_sphere_radius = min(distances)
            if new_sphere_radius > 999: # hit nothing
                break

            if new_sphere_radius < .001:
                print(f'collided after {i} steps')
                break

            sphere.enabled = True
            sphere.scale = new_sphere_radius * 2
            sphere.world_position = current_point.world_position
            current_point.z += new_sphere_radius


app.run()
