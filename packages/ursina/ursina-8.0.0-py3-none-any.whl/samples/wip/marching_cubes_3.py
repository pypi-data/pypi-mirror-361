from ursina import *

app = Ursina()

# for y in range(tex.height):
#     skip = 0
#     for x in range(tex.width):
#
#         if skip > 0:
#             skip -= 1
#             continue
#
#         pixel = color.rgb(*tex.get_pixel(x,y))
#         # print(pixel)
#         if pixel == clear_color:
#             continue
#
#         # print(pixel)
#         b = color.brightness(tex.get_pixel(x,y))
#         # b_right = color.brightness(tex.get_pixel(x+1,y))
#         # b_up = color.brightness(tex.get_pixel(x,y+1))
#         # b_up_right = color.brightness(tex.get_pixel(x+1,y+1))
#
#         j = 0
#
#         for j in range(tex.width-x):
#             if color.rgb(*tex.get_pixel(x+j, y)) != pixel:
#                 break
#
#         verts.extend((
#             (x, b, y),
#             (x +1+j, b, y),
#             (x +1+j, b, y +1),
#             (x, b , y +1)
#             ))
#
#         tris.append((i, i+1, i+2, i+3))
#         # uvs.append((x/tex.width, y/tex.height))
#         # uvs.append(((x+skip) /tex.width, y/tex.height))
#         # uvs.append(((x+skip) /tex.width, (y+skip) /tex.height))
#         # uvs.append((x /tex.width, (y+skip) /tex.height))
#         # colors.extend((pixel, )*4)
#
#         i += 4
#         skip = j




def preview(tex, clear_color=color.white):
    # global preview_model
    print('.........')
    verts = list()
    colors = list()

    for y in range(tex.height):
        for x in range(tex.width):
            pixel = color.rgb(*tex.get_pixel(x,y))

            if pixel == clear_color:
                continue

            neighbors = (
                color.rgb(*tex.get_pixel(x,y+1)),
                color.rgb(*tex.get_pixel(x+1,y)),
                color.rgb(*tex.get_pixel(x,y-1)),
                color.rgb(*tex.get_pixel(x-1,y)),
                )

            if (pixel == neighbors[0]
                and pixel == neighbors[1]
                and pixel == neighbors[2]
                and pixel == neighbors[3]
                ):

                verts.append((x,y,0))
                colors.append(pixel)
                continue

            for z in range(16):
                verts.append((x,y,z))
                if z == 0:
                    colors.append(pixel)
                else:
                    colors.append(pixel.tint(-.2))

    preview_model.model = Mesh(vertices=verts, colors=colors, mode='point', thickness=32)
    preview_model.position =  (-tex.width/2*preview_model.scale_x, ) * 2     # center


def input(key):
    if held_keys['control'] and key == 'r':
        t = time.time()
        preview(tex)
        print('duration:', time.time() - t)


tex = load_texture('pot')
preview_model = Entity(scale=1 / max(tex.size) * 8)

preview(tex)


EditorCamera()
app.run()
