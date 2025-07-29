from ursina import *

app = Ursina()
random.seed(0)

ground = Entity(model='plane', origin=(-.5,0,-.5), scale=64, texture='quad_tree_terrain_heightmap')
ground.texture.filtering = None
EditorCamera()

import copy
# m = Prismatoid(base_shape=Quad(segments=0), path=((0,0,0),(0,1,0)), thicknesses=((1.3,1.3),(1,1)))
m = Prismatoid(base_shape=Circle(resolution=7, radius=1), path=((0,0,0),(0,1,0)), thicknesses=((1.3,1.3),(1,1)))
p=Entity()
def input(key):
    if key in ('space', 'space hold'):
        t = ground.texture
        exit = False

        for y in range(t.height):
            if exit:
                break
            for x in range(t.width):
                if exit:
                    break

                col = t.get_pixel(x,y)
                if col == color.black or col == color.red:
                    continue

                # find biggest square that fits
                for i in range(16):
                    if color.black in t.get_pixels((x,y), (x+i,y+i)):
                        break

                # printvar(i)
                i -= 1
                for _y in range(y, y+i):
                    for _x in range(x, x+i):
                        t.set_pixel(_x, _y, color.black)

                e = Entity(
                    parent=p,
                    model=copy.copy(m),
                    position=(x,0,y),
                    # origin=(-.5,0,-.5),
                    texture='white_cube',
                    scale=(i,4+(random.random()),i),
                    color = color.color(random.uniform(0,90), random.uniform(.2, .5), random.uniform(.9, 1.0)),
                    rotation_y = random.uniform(0,360),
                    )
                e.scale *= 1.1
                t.apply()
                exit = True

    if key == 'b':
        p.combine()
    #     p.model.colorize()

app.run()
