from ursina import *






class TransformGizmo(Draggable):
    def __init__(self, **kwargs):
        super().__init__(
            model='quad',
            scale=1/9/4 * .75,
            step=0,
            origin=(-.5,-.5),
            min_x=-.5*camera.aspect_ratio*.75,
            max_x=.5*camera.aspect_ratio*.75,
            min_y=-.5*.75,
            max_y=.5*.75,
            )

        self.x_axis_ruler = Entity(parent=self, model='quad', scale=(9999,.1), z=.1, color=color.red, alpha=.3)
        self.y_axis_ruler = Entity(parent=self, model='quad', scale=(9999,.1), z=.1, color=color.lime, rotation_z=90, alpha=.3)

        self.right_arrow = Draggable(parent=self, model='quad', origin=(-.5,-.5), color=color.orange, scale_y=.15, scale_x=3, lock_x=True, lock_y=True)
        def horizontal_drag():
            mouse.position = self.position
            self.lock_y = True
            self.dragging = True
        self.right_arrow.drag = horizontal_drag

        self.up_arrow = Draggable(parent=self, model='quad', origin=(-.5,.5), color=color.lime, scale_y=.15, scale_x=3, lock_x=True, lock_y=True, rotation_z=-90)
        def vertical_drag():
            mouse.position = self.position
            self.lock_x = True
            self.dragging = True
        self.up_arrow.drag = vertical_drag

        def drop():
            self.lock_x = False
            self.lock_y = False
            self.dragging = False

        self.right_arrow.drop = drop
        self.up_arrow.drop = drop


        for key, value in kwargs.items():
            setattr(self, key, value)



    def update(self):
        super().update()

        self.x_axis_ruler.enabled = held_keys['x']
        self.y_axis_ruler.enabled = held_keys['y']

        if held_keys['x']:
            self.world_y = self.start_pos[1] # start pos is inherited from Draggable
        if held_keys['y']:
            self.world_x = self.start_pos[0] # start pos is inherited from Draggable



class UIDesigner(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui)
        self.scale *= .75
        self.transform_gizmo = TransformGizmo()
        self.bg = Entity(parent=self, model='quad', scale_x=camera.aspect_ratio, color=window.color, z=100)
        self.grid = Entity(
            parent=self,
            position=window.bottom_left,
            model=Grid(16*8, 9*8),
            scale_x=camera.aspect_ratio,
            z=-100,
            color=color.color(0,0,1,.1),
            enabled=False
            )
        self.snap = False
        self.ui_elements = list()
        self.selection = None
        window.color = color._32

    def input(self, key):
        if key == 'shift':
            self.snap = not self.snap

        if key == 'shift up':
            self.snap = not self.snap

        if key == 's':
            self.snap = not self.snap

        if key == 'b':
            self.add_button()

        if key == 'left mouse down':
            self.transform_gizmo.enabled = mouse.hovered_entity
            self.transform_gizmo.position = self.selection.get_position(relative_to=self)

            if not mouse.hovered_entity and self.selection:
                self.selection.world_parent = self.selection.org_parent
                self.selection = None
                self.transform_gizmo.enabled = False
                return

            if mouse.hovered_entity not in self.ui_elements or mouse.hovered_entity == self.selection:
                return

            self.selection = mouse.hovered_entity

            self.transform_gizmo.z = -100
            self.selection.org_parent = self.selection.parent
            self.selection.org_z = self.selection.z
            self.selection.world_parent = self.transform_gizmo
            print_on_screen('select: ' + self.selection.name)

        if key == 'left mouse up' and self.selection and mouse.hovered_entity == self.transform_gizmo:
            self.selection.world_parent = self.selection.org_parent
            self.selection.z = self.selection.org_z




    @property
    def snap(self):
        return self._snap

    @snap.setter
    def snap(self, value):
        self._snap = value
        if value:
            self.grid.enabled = not self.grid.enabled
            if self.grid.enabled:
                self.transform_gizmo.step = (1/9/8*self.scale_y, 1/9/4*self.scale_y)
        else:
            self.grid.enabled = False
            self.transform_gizmo.step = 0

    def add_button(self):
        self.ui_elements.append(Button(parent=self, scale=(.25,.05), text='Button', ignore=True))




if __name__ == '__main__':
    app = Ursina()
    UIDesigner()
    app.run()
