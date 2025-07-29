from ursina import *



voxel_tool = '''
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


app = Ursina()

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = .5,
            texture = 'white_cube',
            color = color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color = color.lime,
        )


    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal)

            if key == 'right mouse down':
                destroy(self)


for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x,0,z))


player = FirstPersonController()
app.run()
'''
window.color = color.color(220, .23, .15)
tf = TextField()
tf.text_entity.text_colors['default'] = color.color(219, .0, .95)
tf.text_entity.text_colors['class_color'] = color.color(40, .61, .9)
tf.text_entity.text_colors['kw_color'] = color.color(210, .59, .94)
tf.text_entity.text_colors['func_color'] = color.color(250, .46, .87)
tf.text_entity.text_colors['param_clor'] = color.color(30, .71, .92)
tf.text_entity.text_colors['string_color'] = color.color(90, .48, .86)

# tf.text_entity.text_colors['default'] = color._200
# tf.text_entity.text_colors['class_color'] = color._250
# tf.text_entity.text_colors['kw_color'] = color._250
# tf.text_entity.text_colors['func_color'] = color._250
# tf.text_entity.text_colors['param_clor'] = color._250
# tf.text_entity.text_colors['string_color'] = color._250

tf.replacements = {

    'from ':    f'☾kw_color☽from ☾default☽',
    'import ':  f'☾kw_color☽import ☾default☽',
    'def ':     f'☾kw_color☽def ☾default☽',
    'for ':     f'☾kw_color☽for ☾default☽',
    'if ':      f'☾kw_color☽if ☾default☽',
    ' in ':     f'☾kw_color☽ in ☾default☽',

    'print(':   f'☾func_color☽print☾default☽(',
    'range(':   f'☾func_color☽range☾default☽(',
    '__init__': f'☾func_color☽__init__☾default☽',
    'super':    f'☾func_color☽super☾default☽',

    'class ':   f'☾class_color☽class ☾default☽',
    'Entity':   f'☾lime☽Entity☾default☽',
    'self.':    f'☾class_color☽self☾default☽.',
    '(self)':   f'(☾class_color☽self☾default☽)',
    'self,':    f'☾class_color☽self☾default☽,',

    'highlight_color = ':    f'☾param_clor☽highlight_color☾default☽ = ',

    '\',':    f'\',☾default☽',   # end quote
    '\':':    f'\':☾default☽',   # end quote
    '\')':    f'\')☾default☽',   # end quote
    '\'':    f'☾string_color☽\'', # start quote
    }
for name in tf.attributes:
    tf.replacements[f'{name}='] = f'☾param_clor☽{name}☾default☽='
    tf.replacements[f'{name} = '] = f'☾param_clor☽{name}☾default☽ = '

# tf.line_numbers.enabled = True
tf.cursor.enabled = False
tf.add_text(voxel_tool[1:])
tf.text_entity.text = multireplace(tf.text, tf.replacements)
# tf.line_numbers.text = '\n'.join([str(e) for e in range(len(tf.text.split('\n')))])
# tf.line_numbers.color = color.gray
tf.text_entity.enabled = False
tf.bg.enabled = False
# tf.text_entity.appear(speed=.004)
