from ursina import *
import time
#
#
# class Line(Entity()):
#     def __init__(self):
#         super().__init__()
#
#         self.model = 'quad'

app = Ursina()
def update():
    Entity(model=Mesh(vertices=((0,0,0), (1,1,0), (2,3,0), (2,5,0)), mode='line', thickness=3))


app.run()
