'''introducin
ursina

game engine



features:
    powerful
    pythonic
    hotreloading
    no editor, but easily make your own. *show value of life editor*
    procedural models
games:
    bokfall
    platformer
    flying game
    minecraft clone
    otoblop
    amvol
    terrain example
    terrain example 2


Ursina
Make games!
Free and open source!
Code in Python!
'''


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    step = 8.72/8
    window.color=color.black
    window.exit_button.visible = False
    # t = Text(text, scale=2, origin=(0,0), y=.45)
    # for i in range(16):
    #     invoke(setattr, t, 'text', i, delay=i*step)

    intro_text = Text('Introducing', scale=2, origin=(0,0))
    intro_text_2 = Text('Your New \n<azure>GAME ENGINE', scale=2, origin=(0,0), enabled=False)
    logo = Sprite(name='ursina_splash', parent=camera.ui, texture='ursina_logo', world_z=camera.overlay.z-1, scale=.1, color=color.clear)

    # clip_1 = Entity(parent=camera.ui, model='quad', color=color.orange, enabled=False)
    clip_1 = Animation('trailer_screenshot', fps=1/step/2, parent=camera.ui, enabled=False, autoplay=False, scale=1)
    # def update():
    #     clip_1.rotation_z += 5

    text_2 = Text('Make games!', scale=2, origin=(0,0), enabled=False)
    text_3 = Text('Free and open source!', scale=2, origin=(0,0), enabled=False)
    text_4 = Text('Code in Python!', scale=2, origin=(0,0), enabled=False)

    Sequence(
        Func(intro_text.appear, step/len(intro_text.text)/2),
        Wait(step*2),
        Func(intro_text.fade_out),
        Wait(step*.5),

        Func(intro_text_2.appear, step/len(intro_text_2.text)/2),
        Wait(step*1),
        Func(intro_text_2.fade_out),

        Func(logo.animate_color, color.white, duration=step),
        Func(logo.animate_scale, logo.scale*1.25, curve=curve.linear, duration=step*8),
        Wait(step*5),
        Func(logo.animate_color, color.clear, curve=curve.linear, duration=step),
        Wait(step*1),

        Func(setattr, clip_1, 'enabled', True), Func(clip_1.start), Wait(step*8), Func(setattr, clip_1, 'enabled', False),
        Func(setattr, text_2, 'enabled', True), Wait(step*4), Func(setattr, text_2, 'enabled', False),
        Func(setattr, text_3, 'enabled', True), Wait(step*4), Func(setattr, text_3, 'enabled', False),
    ).start()
    # intro = Text('Free and open source', scale=2, origin=(0,0), enabled=False)
    Audio('rocket_ursina_trailer_1')
    # logo.fade_in(delay=4)
    # t = Text('Ursina')

    app.run()
