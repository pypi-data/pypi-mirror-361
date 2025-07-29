from ursina import *
from copy import copy, deepcopy
from pprint import pprint



color.lime = color.color(60, .9, .77)
color.azure = color.color(180, .56, .73)
app = Ursina()
ground_plane = Entity(model='plane', scale=32, origin=(-.5,0,-.5), position=(-.5,0,-.5), collider='box', color=color.azure, visible=False)
water = Entity(model='plane', scale=256, position=(16,-1,16), color=color.azure)
cursor = Entity(model='cube', origin=(-.5,-.5,-.5), scale_y=1, color=color.color(0,1,.8,.3))
fake_ground = Entity(model='plane', scale=36, position=(-.5,.01,-.5), color=color.azure.tint(-.2), origin=(-.5,0,-.5))

fallback = Mesh(
    vertices=[(-.5,0,-.5), (.5,0,-.5), (.5,0,.5), (-.5,0,.5),  (-.5,0,-.5), (.5,0,-.5), (.5,0,.5), (-.5,0,.5), (-.5,-16,-.5), (.5,-16,-.5), (.5,-16,.5), (-.5,-16,.5)],
    triangles=[(0,1,2,3), (4,5,6,7), (4,8,9,5), (5,9,10,6), (6,10,11,7), (7,11,8,4)],
    colors=(color.lime, )*4 + (color.dark_gray, )*8
    )

middle = Mesh(vertices=((-.5,0,-.5), (.5,0,-.5), (.5,0,.5), (-.5,0,.5)), triangles=((0,1,2,3),), colors=(color.lime, )*4)

edge = Mesh(
    vertices=((-.5,0,-.5), (.5,0,-.5), (.5,0,.5), (-.5,0,.5),       (-.5,0,.5), (.5,0,.5), (.5,-1,.5), (-.5,-1,.5)),
    triangles=((0,1,2,3), (4,5,6,7)),
    colors=(color.lime, )*2 + (color.lime.tint(.1), )*2 + (color.dark_gray, )*4
    )

outer_corner = Mesh(
    vertices=((-.5,0,-.5), (.5,0,-.5), (-.5,0,.5),      (-.5,0,.5), (.5,0,-.5), (.5,-1,-.5), (-.5,-1,.5),     (-.5,-1,.5), (.5,-1,-.5), (.5,-1,.5)),
    triangles=((0,1,2), (3,4,5,6), (7,8,9)),
    colors=(color.lime, color.lime.tint(.1), color.lime.tint(.1)) + (color.dark_gray, )*4 +(color.lime, )*3
    )

inner_corner = Mesh(
    vertices=[(-.5,0,-.5), (.5,0,-.5), (.5,0,.5), (-.5,0,.5)],
    triangles=[(0,1,2,3), ],
    colors=(color.lime, color.lime, color.lime.tint(.1), color.lime)
    )
# edge = Entity(model='quad').model

# corner_shape_name = deepcopy(cube)
# corner_shape_name.c
valid_corners = dict()
for e in ('00001110', '00001111', '00011110', '00011111'):
    for i in range(4):
        e = e[i*2:] + e[:i*2]   # rotate
        # valid_corners[e] = i*90
        rotations = (0, -90, 90, 180)
        valid_corners[e] = rotations[i]

valid_edges = dict()
for e in ('00111110', '01111110', '00111111', '01111111'):
    for i in range(4):
        e = e[i*2:] + e[:i*2]   # rotate
        # rotations = (-180, 90, -90, 0)
        rotations = (0, -90, 90, 180)
        valid_edges[e] = rotations[i]



world_size = 32
entities = [[Entity(model=copy(middle), position=(x,0,z), ignore=True, scale_y=1, shape_name='middle') for z in range(world_size)] for x in range(world_size)]
brush_size = 1
target_height = 4
x, z = 0, 0

def get_heights():
    return [[e.y for e in row] for row in entities]

undo_cache = list()
undo_cache.append(get_heights())
undo_index = len(undo_cache)-1

def update():
    global x, y, target_height

    if mouse.hovered_entity == ground_plane:
        cursor.world_position = mouse.world_point
        cursor.x = round(cursor.x)
        cursor.z = round(cursor.z)
        x, z = math.floor(cursor.x), math.floor(cursor.z)
        x, z = clamp(x, 0, world_size-1), clamp(z, 0, world_size-1)
        # cursor.y = entities[x][z].y

        # sample height
        if held_keys['alt'] and mouse.left:
            target_height = entities[x][z].y

        # draw
        elif mouse.left:
            for j in range(brush_size):
                for i in range(brush_size):
                    temp_x, temp_z = clamp(x+i, 0, world_size-1), clamp(z+j, 0, world_size-1)
                    entities[temp_x][temp_z].y = target_height

            find_shape()


def find_shape():
    for z in range(1,world_size-1):
        for x in range(1, world_size-1):
            # check neighbors
            target_height = entities[x][z].y
            n, ne, e, se, s, sw, w, nw = True, True, True, True, True, True, True, True
            n =  entities[x  ][z+1].y >= target_height
            ne = entities[x+1][z+1].y >= target_height
            e =  entities[x+1][z  ].y >= target_height
            se = entities[x+1][z-1].y >= target_height
            s =  entities[x  ][z-1].y >= target_height
            sw = entities[x-1][z-1].y >= target_height
            w =  entities[x-1][z  ].y >= target_height
            nw = entities[x-1][z+1].y >= target_height

            neighbors = ''.join([str(int(e)) for e in (n, ne, e, se, s, sw, w, nw)])
            e = entities[x][z]

            if not '0' in neighbors:    # middle
                if e.shape_name != 'middle':
                    e.shape_name = 'middle'
                    e.model = copy(middle)
                    # e.origin_y=.5

                    # e.color = color.white

            elif neighbors.count('0') == 1 and neighbors.index('0') % 2 == 1:   # inner corner
                if e.shape_name != 'inner_corner':
                    e.shape_name = 'inner_corner'
                    e.model = copy(inner_corner)
                    # e.color = color.orange
                    e.rotation_y = (neighbors.index('0')-1) / 2 * 90

            elif neighbors in valid_edges:    # edge
                if e.shape_name != 'edge':
                    e.shape_name = 'edge'
                    e.model = copy(edge)
                    # e.origin_y=.5
                    e.rotation_y = valid_edges[neighbors]

                    pos = e.position + e.forward
                    bottom_neighbor_height = entities[int(pos[0])][int(pos[2])].y
                    bottom_neighbor_height = e.y - bottom_neighbor_height
                    # Entity(model='sphere', color=color.red, position=e.position + e.forward, y=bottom_neighbor_height)
                    m = eval(edge.recipe)
                    # print('-------------', bottom_neighbor_height, e.y)
                    m.vertices = [Vec3(v[0], -bottom_neighbor_height, v[2]) if v[1] < -.5 else v for v in m.vertices]
                    m.generate()
                    e.model = m
                # e.color = color.lime

            elif neighbors in valid_corners:    # outer corner
                if e.shape_name != 'outer_corner':
                    e.shape_name = 'outer_corner'
                    e.rotation_y = valid_corners[neighbors]
                    # print('-----', valid_corners[neighbors])
                    # print(e.position + e.forward)
                    pos = e.position + e.forward
                    bottom_neighbor_height = entities[int(pos[0])][int(pos[2])].y
                    bottom_neighbor_height = e.y - bottom_neighbor_height
                    # Entity(model='sphere', color=color.red, position=e.position + e.forward, y=bottom_neighbor_height)
                    m = eval(outer_corner.recipe)
                    # print('-------------', bottom_neighbor_height, e.y)
                    #
                    new_verts = list()
                    for v in m.vertices:
                        if v[1] < -.5:
                            new_verts.append(Vec3(v[0], -bottom_neighbor_height, v[2]))
                            continue

                        new_verts.append(v)

                    m.vertices = new_verts
                    m.generate()
                    e.model = m

                    # e.model = copy(outer_corner)
                    # e.origin_y=.5
                    # e.rotation_y = valid_corners[neighbors]
                # e.color = color.red

            else:
                if e.shape_name != 'fallback':
                    e.shape_name = 'fallback'
                    e.model = copy(fallback)


def save(name):
    # print(entities)
    for e in entities[0]:
        print(e.y, )


def load(name):
    # Autoblock()
    pass


def input(key):
    global undo_cache, undo_index, entities, brush_size, target_height, cursor
    if not mouse.left:
        if held_keys['control']:
            if key in ('z', 'z hold') and not held_keys['shift']:
                undo_index -= 1
                undo_index = clamp(undo_index, 0, len(undo_cache)-1)
                for z in range(world_size):
                    for x in range(world_size):
                        entities[x][z].y = undo_cache[undo_index][x][z]

            if held_keys['shift'] and key in ('z', 'z hold') or key in ('y', 'y hold'):
                undo_index += 1
                undo_index = clamp(undo_index, 0, len(undo_cache)-1)
                for z in range(world_size):
                    for x in range(world_size):
                        entities[x][z].y = undo_cache[undo_index][x][z]


        if mouse.hovered_entity == ground_plane and key == 'left mouse up':
            # record undo
            undo_index += 1
            undo_cache = undo_cache[:undo_index]
            undo_cache.append(get_heights())

    if key == 'd':
        brush_size += 1
        brush_size = max(brush_size, 1)
        cursor.scale = (brush_size,1,brush_size)
    if key == 'x':
        brush_size -= 1
        brush_size = max(brush_size, 1)
        cursor.scale = (brush_size,1,brush_size)

    if key == 'q':
        target_height -= 1
        target_height = max(target_height, 0)
    if key == 'e':
        target_height += 1
        target_height = max(target_height, 0)

    if held_keys['control'] and key == 's':
        self.save()



EditorCamera(position=(16,10,16), rotate_around_mouse_hit=False)
# camera.orthographic = True
window.exit_button.visible = False
window.fps_counter.enabled = False
window.color = color.black
app.run()
