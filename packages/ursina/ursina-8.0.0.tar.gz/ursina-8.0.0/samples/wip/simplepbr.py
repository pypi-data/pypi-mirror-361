from ursina import *
# import simplepbr

app = Ursina(pbr=True)
Entity(model='sphere', color=color.red)


EditorCamera()




app.run()
