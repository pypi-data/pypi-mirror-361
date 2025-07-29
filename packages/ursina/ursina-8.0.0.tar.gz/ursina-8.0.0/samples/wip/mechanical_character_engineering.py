from ursina import *
from ursina.color import *

class Gear(Draggable):
    def __init__(self):
        super().__init__(**kwargs)
        print('create gear')
        self.parent = scene
        self.model = 'cylinder'
        self.rotation_x = 90


class Toolbox(Entity):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        # self.origin = (-.5, .5)
        self.position = window.top_left + (.1, -.1)

        button_dict = {
            'create gear' : 'Gear()',
            'create line' : '''print('lol')''',
            }

        for i, e in enumerate(button_dict):
            b = Button(
                parent = self,
                scale = (.2, .05),
                text = e,
                on_click = button_dict[e]
                )

        grid_layout(self.children, max_x=1, direction=(1,-1,0))





if __name__ == '__main__':
    app = Ursina()
    Toolbox()

    # cube = Entity(position=(0,1,0), rotation=(0,0,0), scale_y=2, model='cube', origin_y=-.5)
    #
    # slider = Slider(0, 4, default=1, dynamic=True)
    # slider.label.text = 'cube height'
    # def on_value_changed():
    #     cube.scale_y = slider.value
    #     cube.color = color(slider.value*100, 1, 1)
    # slider.on_value_changed = on_value_changed


    camera.orthographic = True
    EditorCamera()
    app.run()
