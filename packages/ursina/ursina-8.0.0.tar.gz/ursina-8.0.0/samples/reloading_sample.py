from ursina import *

app = Ursina(size=Vec2(1920,1080)*.5)
window.always_on_top = True
window.position = (0, 1080/2)

entity = Entity(model='cube', texture='white_cube')

def update():
    entity.rotation_y += time.dt * 10
    entity.y = sin(time.time() * 3) * .5
    entity.color = hsv(time.time() * 100, 1, 1)

window.color = hsv(0,0,.1)

Entity(model=Grid(8,8), rotation_x=90, y=-1, scale=8, alpha=.2)
EditorCamera()
app.run()
