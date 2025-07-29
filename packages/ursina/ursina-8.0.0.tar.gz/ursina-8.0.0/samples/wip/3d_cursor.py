from ursina import *

app = Ursina()

Entity(model='plane', color=color.salmon, scale=10, collider='box')

cursor = Entity(model=Circle(24, mode='line', thickness=4), rotation_x=90)

def input(key):
    if key == 'left mouse down':
        cursor.position = mouse.world_point
        cursor.y += .1
        cursor.scale = 0
        cursor.animate('scale', Vec3(1,1,1), duration=.2, curve=curve.in_out_circ)
        cursor.color = color.white
        cursor.animate('color', color.clear, duration=.2-.05, delay=.05, curve=curve.in_out_circ)




EditorCamera()


app.run()
