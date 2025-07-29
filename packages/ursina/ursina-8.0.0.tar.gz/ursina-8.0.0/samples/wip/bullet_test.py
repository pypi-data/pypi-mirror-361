from ursina import *
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletBoxShape, BulletRigidBodyNode, BulletDebugNode
from panda3d.core import *
from ursina.shaders import basic_lighting_shader

app = Ursina()

ground = Entity(model='plane', scale=10, texture='grass')
box = Entity(model='cube', color=color.yellow, shader=basic_lighting_shader)

world = BulletWorld()
world.setGravity(Vec3(0, -9.81, 0))


# def Entity():
#     node = BulletRigidBodyNode('Ground')
#     node.addShape(shape)
#     world.attachRigidBody(node)
#     return render.attachNewNode(node)
#

shape = BulletPlaneShape(Vec3(0, 1, 0), 0)
node = BulletRigidBodyNode('Ground')
node.addShape(shape)
np = render.attachNewNode(node)
ground.parent = np
world.attachRigidBody(node)

class RB(NodePath):
    def __init__(self, **kwargs):
        super().__init__('test')
        box_node = BulletRigidBodyNode('Box')
        box_node.setMass(1)

RB()

shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
box_node = BulletRigidBodyNode('Box')
box_node.setMass(1.0)
box_node.addShape(shape)
world.attachRigidBody(box_node)

thing = NodePath(box_node)
thing.reparentTo(render)
thing.set_y(2)
# box.model.reparentTo(thing)
# box_node.reparentTo(thing)
destroy(box)
# thing.clear()
# thing.attachNewNode(box_node)
print('---------', thing.get_nodes())
# box. y = 2
# box_np = NodePath()
# box_np.attachNewNode(box_node)
# box_np = render.attachNewNode(box_node)
# box_np.setY(4)
# box.parent = box_np



Sky()
ed = EditorCamera()
ed.rotation = (20, 10, 0)
ed.y = 1
window.size *= .5
Text('Hold space to simulate physics', position=window.top, origin=(0,1), color=color.black)
debugNode = BulletDebugNode('Debug')
debugNode.showWireframe(True)
debugNode.showConstraints(True)
debugNode.showBoundingBoxes(False)
debugNode.showNormals(False)
debugNP = render.attachNewNode(debugNode)
debugNP.show()
world.setDebugNode(debugNP.node())

def update():
    if held_keys['space']:
        world.doPhysics(time.dt)
        print(thing.node())


app.run()
