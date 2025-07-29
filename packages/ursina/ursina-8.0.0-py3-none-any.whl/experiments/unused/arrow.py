from ursina import *


class Arrow(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.shaft = Entity(
            parent = self,
            model = 'cube',
            scale = (.1, .1),
            origin_z = -.5,
            )
        self.tip = Entity(
            parent = self,
            model = Cone(6),
            z = 1,
            rotation_x = 90,
            scale = .3,
            origin_y = 1
            )

        self.length = 1
        self.end = (0,0,1)


        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self.look_at(value)
        self.length = distance(value, self)
        self.tip.z = self.length
        self.shaft.scale_z = self.length - self.tip.scale_z
        self._end = value



if __name__ == '__main__':
    app = Ursina()
    
    a = Arrow()
    target = Entity(position=(1,1,1))
    a.end = target
    print(a.end)

    origin = Entity(model='quad', color=color.orange, scale=(5, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
