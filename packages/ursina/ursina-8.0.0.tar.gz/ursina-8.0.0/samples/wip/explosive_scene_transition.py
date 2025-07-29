from ursina import *
from ursina import color as ursinacolor


class ExplosiveSceneTransition(Entity):
    def __init__(self, color=ursinacolor.black, **kwargs):
        super().__init__()
        self.world_parent = camera

        for i in range(10):
            e = Entity(
                parent = self,
                # model = Cone(direction=(0,0,1)),
                model = 'sphere',
                scale = random.uniform(.5, 2),
                scale_z = 20,
                origin_z = -.5,
                color = ursinacolor.clear,
                z = -1
                )
            e.look_at((
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
                ))
            e.animate_scale_z(0, .3, delay=random.uniform(0,.2))
            e.animate_color(color, delay=.3)
            e.fade_out(duration=.5)
            window.overlay.fade_in(.4, delay=.4)
            # e.animate_scale((0,0,0), .3, delay=random.uniform(.2,.5))
        for i in range(3):
            c = Entity(
                parent = self,
                model = Circle(24),
                scale = 0,
                color = color,
                z = -5
                )
            c.animate_scale(Vec3(i+1,i+1,i+1)*6, duration=i/10 +.1, delay=.5, curve=curve.in_bounce)

        # window.overlay.fade_out(delay=1)
        destroy(self, delay=1)

if __name__ == '__main__':
    app = Ursina()
    random.seed(0)
    ExplosiveSceneTransition(color=color.black)
    app.run()
