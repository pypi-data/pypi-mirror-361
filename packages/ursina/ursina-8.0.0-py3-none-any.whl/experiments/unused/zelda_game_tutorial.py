from ursina import *

# window.set_z_order(window.Z_top)
app = Ursina()
# window.position=(1920/2, 0)
# window.size = (1920/2, 1080/2)

# ok guys, let's start by creating a ground, uwu
# ground = Entity()
# and set the model by giving it the name of our model.
#let's just use the included 'plane' model for now.
# ground = Entity(model='plane')
# scale it up and give it a color.
class Test(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.ground = Entity(model='plane', scale=10, color=color.green)
        self.player = Entity(model='cube', scale_y=2, origin_y=-.5, color=color.azure)

        for key, value in kwargs.items():
            setattr(self, key, value)
# set the camera position so we can see better.
# camera.position = (1,10,-20)
# camera.look_at(ground)
# EditorCamera(eternal = True)
# camera.add_script(SmoothFollow(target=player, offset=(0,3,-20)))

    def update(self):
        self.player.x += held_keys['d'] * time.dt
        self.player.x -= held_keys['a'] * time.dt
        #
        # if t > 1:
        #     application.hot_reloader.reload_code()
        #     t = 0

Test()

app.run()
