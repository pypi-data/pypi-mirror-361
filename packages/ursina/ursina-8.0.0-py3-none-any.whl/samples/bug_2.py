from ursina import *

app = Ursina()

m = Mesh(vertices=(Vec3.up, Vec3.right, Vec3.left), uvs=(Vec2.zero, Vec2.zero, Vec2.zero))
Entity(model=m)

app.run()