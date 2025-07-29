from ursina import *
from ursina.prefabs.primitives import *


# class Arild(Entity):
    # def __init__(self):
    #     super().__init__()

    # def create_gear(self):
class Gear(Draggable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('yo')
        self.parent = scene
        self.model = 'sphere'
        # self.model = Cylinder(12, direction=(0,0,1))

        self.collider = 'sphere'

        self.joint = RedCube(parent=self, y=.5)
        self.joint.scale *= .1
        # self.model=Cylinder(6),

    def input(self, key):
        super().input(key)
        if not self.hovered:
            return

        if key == 'scroll down':
            self.scale *= .9
        if key == 'scroll up':
            self.scale /= .9

    def update(self):
        super().update()
        if self.hovered and held_keys['r']:
            if mouse.left:
                self.rotation_z += 2
            if mouse.right:
                self.rotation_z -= 2

        self.color = color.color(60, self.scale_x/4, 1)


    # Entity(model=Cylinder(6), color=color.color(60,1,1,.3))
    # return Gear()


# def create_rod(self):
class Rod(Entity):
    def __init__(self):
        super().__init__()
        self.parent = scene
        self.model = 'cube'
        self.color = color.red
        self.origin = (0, -.5, 0)
        self.scale = (.2, 1, .2)

    def update(self):
        if hasattr(self, 'position_target'):
            self.world_position = self.position_target.world_position

        if hasattr(self, 'look_at_target'):
            self.look_at(self.look_at_target)

    # return Rod()



if __name__ == '__main__':
    app = Ursina()
    # a = Arild()
    # DebugMenu(target=Arild(), position=(-.7, .3))
    # gear = Gear()
    # rod = Rod()
    # rod.position_target = gear.joint
    # g2 = Gear(scale=(.2,.2,.2), position=(0,1,0))
    # rod.look_at_target = g2
    # look_target = a.create_gear()
    # rod.add_script()
    # cube = Entity(position=(0,1,0), rotation=(0,0,0), scale_y=2, model='cube', origin_y=-.5)

    # slider = Slider(0, 4, default=1, dynamic=True)
    # slider.label.text = 'cube height'
    # def on_value_changed():
    #     cube.scale_y = slider.value
    #     cube.color = color(slider.value*100, 1, 1)
    # slider.on_value_changed = on_value_changed


    line0 = Button(parent=scene, model='cube', scale=(.1,.3,.1), origin=(0,-.5,0), color=color.red)
    line0.end = RedCube(parent=line0, y=1, world_scale=(.1,.1,.1))
    line0.end.scale *= 1.1

    line2 = Entity(position=(1.2,-.5), model='cube', scale=(.1, .1, 1), origin=(0,0,-.5), color=color.orange)
    line2.paused = False
    line2.end = Entity(parent=line2, z=1)

    line1 = Entity(model='cube', scale=(.1,.1,1), origin=(0,0,-.5), color=color.green)
    line1.paused = False
    line1.end = Entity(parent=line1, z=1)

    intersecting_point = Entity(model='sphere', scale=(.1,)*3, color=color.cyan)
    def intersect_update():
        line1.world_position = line0.end.world_position
        line2.look_at(line1.world_position)
        line1.look_at(line2.end)

        for i in range(360):
            dist = distance(line1.end.world_position, line2.end.world_position)
            if dist < .1:
                # print('YAY!', dist)
                break
            else:
                line1.rotation_x -= 1
                line2.rotation_x -= 1

        trail = WhiteCube()
        trail.scale *= .05
        trail.origin_z = -.5
        trail.world_position = line1.world_position + (line1.forward * .5)
        destroy(trail, 1)

    intersecting_point.update = intersect_update

    slider = Slider(0, 4, default=1, dynamic=True, y=-.4)
    slider.label.text = 'cube height'
    def on_value_changed():
        line2.scale_z = slider.value
    slider.on_value_changed = on_value_changed

    class Motor(Entity):
        def __init__(self, motor):
            self.motor = motor
            super().__init__()

        def update(self):
            self.motor.rotation_z += held_keys['d'] * 2
            self.motor.rotation_z -= held_keys['a'] * 2

    Motor(line0)

    EditorCamera()
    camera.orthographic = True
    camera.fov = 10
    app.run()
