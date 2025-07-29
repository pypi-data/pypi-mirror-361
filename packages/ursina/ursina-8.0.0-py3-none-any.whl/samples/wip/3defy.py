from ursina import *
from psd_tools import PSDImage
from PIL import Image, ImageFilter
from panda3d.core import Texture as PandaTexture
import copy


app = Ursina()
camera.orthographic = True
camera.fov = 2
# # Sprite('pot')
psd = PSDImage.load(application.textures_folder / 'pot.psd')
image = psd.as_PIL().convert("RGBA")
image = image.transpose(Image.FLIP_TOP_BOTTOM)

mask_color = (255,255,255,255)

def replace_color(image, color, new_color):
    pixel_data = image.load()
    count_replaced = 0

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            if pixel_data[x,y] == (255,255,255,255):
                pixel_data[x,y] = (255, 255, 255, 0)
                count_replaced += 1

    return count_replaced

# verts = list()
# pixel_data = image.load()
# for y in range(image.height):
#     for x in range(image.width):
#         if pixel_data[x,y] != mask_color:
#             # check if pixel is outer corner
#             blank_neighbours = 0
#             for offset in ((0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)):
#                 if pixel_data[x+offset[0], y+offset[1]] == mask_color:
#                     blank_neighbours += 1
#                     if blank_neighbours >= 3:
#                         verts.append((x,y))
#                         break

# marching squares
shapes = {
    # flat sides
    # '1111' : ((0,0), (1,0), (1,1), (0,1)),
    '0111' : ((1,1), (0,1)),    # top
    '1011' : ((1,0), (1,1)),    # right
    '1101' : ((0,0), (1,0)),    # bot
    '1110' : ((0,1), (0,0)),    # left
    # corners
    '0011' : ((1,0), (0,1)),
    '1001' : ((0,0), (1,1)),
    '1100' : ((1,0), (0,1)),
    '0110' : ((0,0), (1,1)),
    }

# loners
shapes['0010'] = shapes['0111']
shapes['0001'] = shapes['1011']
shapes['1000'] = shapes['1101']
shapes['0100'] = shapes['1110']

# Entity(model=Mesh(vertices=verts, mode='point', thickness=5))
# replace_color(image, mask_color, ((255, 255, 255, 0)))
contour = list()

for y in range(1, image.height-1):
    for x in range(1, image.width-1):
        if pixel_data[x, y] == mask_color:
            continue
        neighbours = (
            pixel_data[x, y+1] != mask_color,
            pixel_data[x+1, y] != mask_color,
            pixel_data[x, y-1] != mask_color,
            pixel_data[x-1, y] != mask_color,
            )
        neighbours = ''.join([str(int(e)) for e in neighbours])
        if neighbours in shapes:
            for v in shapes[neighbours]:
                contour.append((x + v[0], y + v[1], 0))


# e =  Entity(model='quad', texture=Texture(image))
e2 = Entity(model=Mesh(vertices=contour, mode='line', thickness=5), scale=1/32, z=-.1, color=color.lime, position=(-.5,-.5))

# e =  Entity(model='quad', texture=Texture(inset), z = 1, color=color.gray)

# for i in range(1,5):
#     image = copy.copy(image)
#     image = image.filter(ImageFilter.MaxFilter(3))
#
#     inset = copy.copy(image)
#     inset = inset.filter(ImageFilter.MaxFilter(1))
#     inset = inset.load()
#     # replace_color(image, mask_color, ((255, 255, 255, 0)))
#
#     pixel_data = image.load()
#     for y in range(image.height):
#         for x in range(image.width):
#             if inset[x,y] != mask_color:
#                 print(inset[x,y])
#                 pixel_data[x,y] = (255,255,255,255)
#
#             # print(inset[x,y] == (0,0,0,0))
#
#     amount_replaced = replace_color(image, mask_color, ((255, 255, 255, 0)))
#     if amount_replaced == 0:
#         continue
#
#     e =  Entity(model='quad', texture=Texture(image))
#     # image = tex._cached_image
#     e.texture.apply()
#     e.z = -i / 32
#     e.color = color.color(0,0,i/8)

EditorCamera()
app.run()
