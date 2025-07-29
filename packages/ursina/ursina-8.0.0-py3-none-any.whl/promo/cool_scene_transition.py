from ursina import *


class CoolSceneTransition():
    def __init__(self, **kwargs):
        self.pivot = Entity(parent=camera.ui, z=-10)
        self.top = Entity(parent=self.pivot, model='quad', origin=(0,-.5), color=color.black, scale=(3,3))
        self.edge = Entity(parent=self.top, model='quad', origin_y=-.5, color=color._20, world_scale_y=.5)
        self.bot = duplicate(self.top)
        self.bot.rotation_z = 180

        self.top.y = .5
        self.bot.y = -.5

    def play(self, speed=1):
        # Sequence.default_time_step = 1/60
        self.top.animate_y(0, duration=1*speed)
        self.bot.animate_y(0, duration=1*speed)
        self.pivot.animate_rotation_z(90, duration=2*speed, curve=curve.in_out_expo, delay=.5*speed)

        if hasattr(self, 'on_close'):
            invoke(self.on_close, delay=1.1*speed)
            
        @after(2*speed)
        def close():
            self.top.animate_y(1, duration=.5*speed)
            self.bot.animate_y(-1, duration=.5*speed)

        # destroy(self.pivot, delay=4)
        # Sequence.default_time_step = None

    # def on_close(self):
    #     print('close')

if __name__ == '__main__':
    app = Ursina()

    # window.color = color.orange
    # window.size *= .35
    # window.center_on_screen()
    cool_scene_transition = CoolSceneTransition()

    def input(key):
        if key == 'space':
            cool_scene_transition.play()

    def on_close():
        window.color = color.olive

    cool_scene_transition.on_close = on_close

    app.run()
