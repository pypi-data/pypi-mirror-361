from ursina import *


app = Ursina()


# e = Entity(model='terrain_1', scale=(20,5,40), texture='heightmap', texture_scale=(4,4))
e = Entity(model=Terrain('heightmap_1', skip=1), scale=(20,5,20), texture='heightmap', texture_scale=(2,2))
EditorCamera()
Sky()
app.run()
