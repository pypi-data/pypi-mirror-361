from ursina import *
app  = Ursina()

m = model=Mesh(vertices=load_model('quad', use_deepcopy=True).vertices, mode='point', thickness=10)
e = Entity()
# e.setShaderAuto()
e.model = m
EditorCamera()
Entity(model='plane', color=color.black, scale=10)
print(e.shader)
app.run()