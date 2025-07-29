from ursina import *



app = Ursina()

head = Entity(model='sphere', scale=1, scale_x=.9)
jaw = Entity(model=Cylinder(12), position=(0,-.5, -.15), scale=(.8,.5,.7))
jaw.model.generate_normals()

nose = Entity(model='cube',)


window.display_mode = 'normals'

EditorCamera()
app.run()
