from ursina import *

app = Ursina()
voxels = list()

blank = '00000\n' * 5
blank = [[bool(i=='1') for i in e] for e in blank.strip().split('\n')]
print(blank)

slice = '''
00000
01110
01110
01110
00000
'''
slice = [[bool(i=='1') for i in e] for e in slice.strip().split('\n')]
# TODO: add empty space around

plane = [(0,0,0), (1,0,0), (1,1,0), (0,0,0), (0,1,0), (1,1,0)]
plane = [Vec3(e) for e in plane]
plane = [e - Vec3(.5,.5,.5) for e in plane]
right_plane = Entity(model=Mesh(plane), color=color.white33, double_sided=True)
for v in plane:
    Entity(parent=right_plane, position=v, scale=.1, model='cube', color=color.red)


# shapes = {
#     '011111' : get_verts((1,0,0)),     # flat
#     '101111' : get_verts((-1,0,0)),
#     '110111' : get_verts((0,1,0)),
#     '111011' : get_verts((0,-1,0)),
#     # ''          # edge
#     # ''          # outer corner
#     # ''          # inner corner
# }
verts = list()
mesh = Mesh(vertices=verts)
result = Entity(model=mesh)

def add_flat(direction=(0,0,1)):
    print('adding', direction)
    right_plane.look_at(direction, 'back')
    # [verts.append(c.world_position) for c in right_plane.children]
    for c in right_plane.children:
        verts.append(c.world_position)
        # print(c.world_position)
        # invoke(setattr, c, 'color', color.green, delay=i*.5)
        # invoke(setattr, c, 'color', color.red, delay=(i*.5)+.1)

    mesh.vertices = verts
    mesh.generate()


voxels = (blank, slice, slice, slice, blank)
dir_dict = {'11':0, '01':1, '10':-1}

i = 0
for z in range(len(voxels)):
    for y in range(len(voxels[0])):
        for x in range(len(voxels[0][0])):
            if not voxels[x][y][z]:
                continue

            neighbours = (
                voxels[x+1][y][z],
                voxels[x-1][y][z],
                voxels[x][y+1][z],
                voxels[x][y-1][z],
                voxels[x][y][z+1],
                voxels[x][y][z-1],
                )
            neighbours = ''.join([str(int(e)) for e in neighbours])
            # if neighbours in shapes:
            if neighbours.count('0') == 1:
            # print(len(shapes[neighbours]))
                direction=(dir_dict[neighbours[0:2]], dir_dict[neighbours[2:4]], dir_dict[neighbours[4:6]])
                invoke(add_flat, direction, delay=i*.05)
            # for v in shapes[neighbours]:
            #     verts.append(v)
            #     print(v)
            i += 1




print(verts)
# cube_verts = ((0,0,0), (1,0,0), (0,0,1), (1,0,1), (0,1,0), (1,1,0), (0,1,1), (1,1,1))
# cube_tris =  ((0,2,3,1), (0,1,5,4), (1,3,7,5), (3,2,6,7), (2,0,4,6), (5,7,6,4))
# tris = list()
# for e in cube_tris:
#     tris.append((e[0],e[1],e[2]))
#     tris.append((e[2],e[3],e[0]))

# print(tris)
# Entity(model=Mesh(vertices=verts))
# Entity(model=Mesh(vertices=cube_verts, triangles=tris))
EditorCamera()


# def bevel_point(verts, tris, index, amount=.5):
#     connected_points = list()
#     # for i in range(len(verts)):
#     #     if i == index:
#     #         continue
#     connected_tris = [t for t in tris if index in t]
#     for tri in connected_tris:
#         for vertex_index in tri:
#             if not vertex_index == index:
#                 # print(verts[vertex_index])
#                 pos = lerp(verts[index], verts[vertex_index], amount)
#                 Entity(model='cube', scale=.05, color=color.red, position=pos)
#
#     # printvar(connected_tris)
# bevel_point(cube_verts, tris, 1)

app.run()
