from ursina import *

app = Ursina()

window.color = color.color(0, 0, .1)
# scene = '<white>\n' + ((('角' * 20) + '\n') * 20)
water = '___              ~' #'床壁'
tiles = ' ___'
tiles = [char for char in tiles]
scene = '<white>\n'
for y in range(40):
    for x in range(80):
        scene += random.choice(tiles)
    scene += '\n'
# 壁 wall
# 床 floor
printvar(scene)
t = Text(
    font = 'SourceHanSans-Normal.otf',
    # font = 'Inconsolata-Regular.ttf',
    # font = 'VeraMono.ttf',
    text = scene,
    parent = camera.ui,
    position = (-.0 * window.aspect_ratio, .475),
    scale = (.05, .05),
    align = 'center',
    # color = color.red,
    # line_height = .1,
    )
# t.wordwrap = 1000
# t.font = 'VeraMono.ttf'
t.font.setPixelsPerUnit(160)
# t.line_height = .2
# from panda3d.core import TextFont
# t.font.setRenderMode(TextFont.RMSolid)
# t.color = color.gray
class Rouge(Text):
    def __init__(self):
        super().__init__()
        self.font = 'SourceHanSans-Normal.otf'
        self.text = '<red>猫'    # cat
        self.parent = camera.ui
        self.scale = (.05, .05, -1)
        self.scale *= .5
        self.align = 'center'
        self.font.setPixelsPerUnit(160)

    def input(self, key):
        if key == 'd' or key == 'd hold':
            self.x += .05
        elif key == 'a' or key == 'a hold':
            self.x -= .05
        elif key == 'w' or key == 'w hold':
            self.y += .05
        elif key == 's' or key == 's hold':
            self.y -= .05

        if key == 'space' or key == 'space hold':
            e = Entity(
                model = 'quad',
                color = color.red,
                parent = self,
                origin = (-.0, -.5)
                )
            e.reparent_to(self.parent)

p = Rouge()
p.scale *= 2
p. position = (.025, -.03)

app.run()
