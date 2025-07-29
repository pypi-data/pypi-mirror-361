from ursina import *



app = Ursina()

ground_plane = Entity(model='plane', scale=10, collider='box')

class Node(Draggable):
    def __init__(self, **kwargs):
        super().__init__(
            parent=scene,
            model='sphere',
            # origin_y=-.5,
            # position=mouse.world_point,
            color=color.orange,
            rotation_x=90
        )

        self.temp_arrow = Entity(parent=self, model='cube', scale=.05, origin_z=-.5, color=color.red, x=.1)
        self.connections = list()
        self.connecting = False

        self.arrows = list()


        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == 'c' and self.hovered:
            self.connecting = True

        if self.connecting and key == 'c up' and isinstance(mouse.hovered_entity, Node) and mouse.hovered_entity is not self:
            print('connect')
            self.connecting = False
            self.connections.append(mouse.hovered_entity)

            arrow = Button(parent=self, model='cube', scale=.05, origin_z=-.5, color=color.green, collider='box')
            arrow.scale_z = distance(self, mouse.hovered_entity)
            arrow.look_at(mouse.hovered_entity)
            arrow.target = mouse.hovered_entity
            self.arrows.append(arrow)

            def break_connection(arrow=arrow):
                arrow.parent.connections.remove(arrow.target)
                arrow.parent.arrows.remove(arrow)
                destroy(arrow)

            arrow.on_click = break_connection

        # if held_keys['alt'] and key == 'left key down' and mouse.hovered_entity in self.arrows:
        #     self.connections.remove(mouse.hovered_entity.target)
        #     self.arrows.remove(mouse.hovered_entity)
        #     destroy(mouse.hovered_entity)


    def update(self):
        self.temp_arrow.enabled = self.connecting
        if self.connecting:
            self.color = color.green
            self.temp_arrow.look_at(mouse.world_point)
            self.temp_arrow.scale_z = distance(self.world_position, mouse.world_point)
        else:
            self.color = color.orange

def input(key):
    if held_keys['control'] and key == 'left mouse down':
        Node(world_position=mouse.world_point)


    if key == 'f':
        for e in scene.entities:
            if isinstance(e, Node):
                print(e.connections)
# def update():
#     print(mouse.world_point)



EditorCamera()





app.run()
