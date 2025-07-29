from ursina import *


app = Ursina()

e = Entity(model='quad', texture='heightmap')
tex = load_texture('brick')
print('----------------', tex)

verts = list()
tris = list()
colors = list()
uvs = list()

skip = 10
i = 0
for y in range(0, e.texture.height-skip, skip):
    for x in range(0, e.texture.width-skip, skip):
        c = e.texture.get_pixel(x,y)
        # nc = e.texture.get_pixel(x+1, y)
        # verts.append((x/skip, color.brightness(e.texture.get_pixel(x,y+1)), (y/skip +1)))
        # verts.append((x/skip, color.brightness(c), y/skip))
        #
        # colors.append(e.texture.get_pixel(x,y+1))
        # colors.append(c)

        verts.append((x/skip, color.brightness(c), y/skip))
        verts.append(((x/skip) +1, color.brightness(e.texture.get_pixel(x+skip,y)), y/skip))
        verts.append(((x/skip) +1, color.brightness(e.texture.get_pixel(x+skip,y+skip)), (y/skip) +1))
        verts.append((x/skip, color.brightness(e.texture.get_pixel(x,y+skip)), (y/skip) +1))

        # verts.append((x/skip, color.brightness(c), y/skip))
        # verts.append(((x/skip) +1, color.brightness(e.texture.get_pixel(x+skip,y+skip)), (y/skip) +1))
        # verts.append((x/skip, color.brightness(e.texture.get_pixel(x,y+skip)), (y/skip) +1))

        for t in (0,1,2, 0,2,3):
            tris.append(i+t)

        uvs.append((x/e.texture.width, y/e.texture.height))
        uvs.append(((x+1) /e.texture.width, y/e.texture.height))
        uvs.append(((x+1) /e.texture.width, (y+1) /e.texture.height))
        uvs.append((x /e.texture.width, (y+1) /e.texture.height))
        #
        # uvs.append((x /e.texture.width, y /e.texture.height))
        # uvs.append(((x+1) /e.texture.width, (y+1) /e.texture.height))
        # uvs.append((x /e.texture.width, (y+1) /e.texture.height))

        # uvs.append((0,0))
        # uvs.append((1,0))
        # uvs.append((1,1))
        # uvs.append((0,1))
        #
        # uvs.append((0,0))
        # uvs.append((1,1))
        # uvs.append((0,1))

        # for j in range(4):
        # colors.append(c)
        # colors.append(e.texture.get_pixel(x+skip,y))
        # colors.append(e.texture.get_pixel(x+skip,y+skip))
        # colors.append(e.texture.get_pixel(x,y+skip))

        i += 4
        # print((x /e.texture.width, (y) /e.texture.height))

# e.model = Mesh(vertices=verts, colors=colors, mode='tristrip')
e.model = Mesh(vertices=verts, triangles=tris, colors=colors, uvs=uvs, mode='triangle')
e.texture = 'heightmap'
# e.double_sided = False
e.scale_y *= 10
e.scale *= .08
Sky()
EditorCamera()

class Water(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'plane'
        self.scale *= 100
        # self.color=color.red
        self.texture ='default_sky'
    def update(self):
        self.y += held_keys['up arrow'] * .005
        self.y -= held_keys['down arrow'] * .005
Water()

# window.size = (450, 450/window.aspect_ratio)
# VideoRecorder()
app.run()
