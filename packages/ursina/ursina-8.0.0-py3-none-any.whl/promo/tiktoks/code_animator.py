from ursina import *
from ursina.prefabs.text_field import TextField


app = Ursina()
# app = Ursina(forced_aspect_ratio=16/9)

window.position=(0,0)
window.size = Vec2(1080,1920)*.5

window.color = color.hex('#282c34')
Text.default_font = 'VeraMono.ttf'
text_editor = TextField(register_mouse_input=True, line_height=1.3, x=-.25, y=.25, active=False, ignore=True)
text_editor.line_numbers.enabled=True
text_editor.bg.color = window.color

text_editor.text_entity.text_colors['default'] = color.hex('#abb2bf')
text_editor.text_entity.text_colors['cyan'] = color.hex('#61afef')
text_editor.text_entity.text_colors['purple'] = color.hex('#c678dd')
text_editor.text_entity.text_colors['orange'] = color.hex('#d19a66')
text_editor.text_entity.text_colors['string_color'] = color.hex('#98c379')
text_editor.text_entity.text_colors['red'] = color.hex('#e06c75')
text_editor.text_entity.text_colors['gray'] = color.hex('#5c6370')
text_editor.line_numbers.color = lerp(color.hex('#5c6370'), window.color, .5)

for e in range(10):
    text_editor.replacements[f' {e}'] = f' ☾orange☽{e}' # numbers
    text_editor.replacements[f'={e}'] = f'=☾orange☽{e}' # numbers
    text_editor.replacements[f'.{e}'] = f'☾orange☽.{e}' # numbers
    text_editor.replacements[f'-{e}'] = f'☾orange☽-{e}' # numbers
    text_editor.replacements[f'({e}'] = f'(☾orange☽{e}' # numbers


text_editor.replacements.update({
    **{f'{e}': f'☾cyan☽{e}' for e in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'},

    'from ':    f'☾purple☽from ☾default☽',
    'import ':  f'☾purple☽import ☾default☽',
    'def ':     f'☾purple☽def ☾default☽',
    'for ':     f'☾purple☽for ☾default☽',
    'if ':      f'☾purple☽if ☾default☽',
    'with ':    f'☾purple☽with ☾default☽',
    ' in ':     f'☾purple☽ in ☾default☽',

    '\',':    f'\'☾default☽,',   # end quote
    '\':':    f'\':☾default☽',   # end quote
    '\')':    f'\')☾default☽',   # end quote
    '\']':    f'\'☾default☽]',   # end quote
    ' \'':    f' ☾string_color☽\'', # start quote
    '=\'':    f'=☾string_color☽\'', # start quote
    '(\'':    f'(☾string_color☽\'', # start quote
    '[\'':    f'[☾string_color☽\'', # start quote

    '=':        f'☾purple☽=☾default☽',
    '+':        f'☾purple☽+☾default☽',
    '-':        f'☾purple☽-☾default☽',
    '*':        f'☾purple☽*☾default☽',

    'print(':   f'☾func_color☽print☾default☽(',
    'range(':   f'☾func_color☽range☾default☽(',
    '__init__': f'☾func_color☽__init__☾default☽',
    'super':    f'☾func_color☽super☾default☽',

    'update(':   f'☾cyan☽update☾default☽(',
    'input(':    f'☾cyan☽input☾default☽(',

    'class ':   f'☾class_color☽class ☾default☽',
    'self.':    f'☾class_color☽self☾default☽.',
    '(self)':   f'(☾class_color☽self☾default☽)',
    'self,':    f'☾class_color☽self☾default☽,',

    '.':    f'.☾red☽',
    ' ':    f' ☾default☽',
    '(':    f'☾default☽(',
    ')':    f'☾default☽)',
    ', ':    f'☾default☽, ',
    })

code_sections = []
comment_sections = []

with open('how_to_move_forward.py', encoding='utf8') as f:
# with open('rotate_camera_around_point.py', encoding='utf8') as f:
    lines = f.read().split('\n')
    lines = [e for e in lines if not e.strip().endswith('#!hide') if e]

    mode = 'code'
    text = ''

    for i, l in enumerate(lines):
        if mode == 'code' and l.strip().startswith('#'):
            if text:
                code_sections.append(text)
            text = ''
            mode = 'comment'

        elif mode == 'comment' and not l.strip().startswith('#'):
            if text:
                comment_sections.append(text)
            text = ''
            mode = 'code'

        text += l + '\n'

    if mode == 'comment' and text:
        comment_sections.append(text)
    if mode == 'code' and text:
        code_sections.append(text)


parts = list(zip(comment_sections, code_sections))

i = 0
seq = None
def input(key):
    if key == 'space':
        show_next()


def show_next():
    global i, seq
    if i >= len(parts):
        return

    text_editor.render()

    if seq:
        seq.finish()

    text_editor.animate_y(.05+ text_editor.text.count('\n')*.025*text_editor.line_height, duration=1, curve=curve.in_out_cubic)
    def add_text(char):
        text_editor.text += char
        text_editor.render()

    seq = Sequence(
        Wait(1),
        # Func(add_text, parts[i][0]+'\n'),
        # Wait(len(parts[i][0])*.0125),
        )
    for char in parts[i][0]:
        seq.append(Func(add_text, char))
        seq.append(.025)
    seq.append(Func(add_text, '\n'))
    seq.append(Wait(.5))

    for char in parts[i][1]:
        seq.append(Func(add_text, char))
        seq.append(.05)

    seq.append(Func(add_text, '\n'))
    seq.append(Wait(.5))
    seq.append(Func(show_next))
    seq.start()

    i += 1
    print(i)

app.run()
