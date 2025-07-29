from ursina import *

import numpy as np
import mcubes

app = Ursina()
# voxels = list()

# print(blank)

slice = '''
000000000000000000000
011111110000000000000
011111110000000000000
011001111111111111110
011001111111111111110
011001111111111111110
011111110000000000000
011111110000000000000
000000000000000000000
'''
# Entity(model='cube', texture='pot')
t = load_texture('pot')
slice = ''
for row in t.pixels:
    new_row = list()

    for p in row:
        col = color.rgba(*p)
        if col == color.white:
            slice += '0'
        else:
            slice += '1'

    slice += '\n'


print(slice)
slice = [[bool(i=='1') for i in e] for e in slice.strip().split('\n')]

blank = (('0'*len(slice[0])) + '\n') * len(slice)
print(blank)
blank = [[bool(i=='1') for i in e] for e in blank.strip().split('\n')]

voxels = (blank, slice, slice, slice, blank)

# Create a data volumecmd
X, Y, Z = np.mgrid[:len(slice[0]), :len(slice), :4]
# u = (X-15)**2 + (Y-15)**2 + (Z-15)**2 - 8**2
u = np.array(voxels)
# print(u)

# Extract the 0-isosurface
vertices, triangles = mcubes.marching_cubes(u, 0)
vertices, triangles = vertices.tolist(), triangles.tolist()
# print(vertices, triangles)

e = Entity(model=Mesh(vertices, triangles, mode='triangle'))
e.model.colorize()
for c in e.model.colors:
    if c != c:
        print('lol')
    print(c)
# e.reflectivity = 1
# e.flip_faces()
e.scale = .1
e.scale_y *= -1
EditorCamera()
app.run()
# # Export the result to sphere.dae
# mcubes.export_mesh(vertices, triangles, "sphere.dae", "MySphere")
