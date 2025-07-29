from ursina import *
from pathlib import Path
# app = Ursina()


# img = load_texture('background_header.png')
# Entity(model='quad', texture=img, scale=[img.width/100, img.height/100])
# bg = Entity(model='quad', scale=[img.width/100, img.height/100], z=.1)
#
# for y in range(img.height):
#     for x in range(img.width):
#         col = img.get_pixel(x,y)
        # print(col)
        # new_color = hsv(col.h, col.s, col.v)
        # img.set_pixel()

# img.apply()
# app.run()
from ursina.ursinamath import chunk_list
from PIL import Image
#
# path = Path('.').parent.parent.parent / 'docs' / 'background_header.png'
# print(path)
img = Image.open('background_header.png')
palette = img.getpalette()
# print(palette)
palette = list(chunk_list(palette, 3))
w, h = img.size

for y in range(h):
    for x in range(w):
        palette_index = img.getpixel((x, y))
        col = palette[palette_index]
        col = color.rgb(*col)
        print(col)
