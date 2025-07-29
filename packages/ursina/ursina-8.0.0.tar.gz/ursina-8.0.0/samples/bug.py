from ursina import *

app = Ursina(vsync=False)

Entity(model='ursina_logo_wireframe')
EditorCamera()

app.run()