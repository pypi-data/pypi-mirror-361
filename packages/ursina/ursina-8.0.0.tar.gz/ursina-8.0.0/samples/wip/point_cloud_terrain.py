from ursina import *

window.vsync = False
app = Ursina()

application.asset_folder = application.asset_folder.parent
ground = Entity(model='plane', texture='heightmap_1', scale=512/20)

EditorCamera()

tex = ground.texture
verts = list()
vert_colors = list()
step = 10
t = time.time()
for z in range(tex.height // step):
    for x in range(tex.width // step):
        p = tex.get_pixel(x*step, z*step)
        h = int(color.brightness(p) * 10)
        # print(p)
        # z = y
        # verts += (
        #     (x,0,z), (x+1,0,z), (x+1,h,z), (x,0,z), (x+1,h,z), (x,h,z),
        #
        # )
        # verts.append(Vec3(x,h,z))
        # col = color.rgb(p[0], p[1], p[2])
        # col = color.tint(col, (z/255/2)-.2)
        # vert_colors += (lerp(p, color.random_color(), .1), )
        for y in range(0, h, 1):
            verts.append(Vec3(x, y, z))
            col = p.tint(random.uniform(-.01,.01))
            vert_colors.append(col)

print(time.time()-t)
scale = .2
e = Entity(model=Mesh(vertices=verts, colors=vert_colors, mode='point', render_points_in_3d=True, thickness=.75, static=True), scale=scale,
    texture='circle'
    )

for i in range(10):
    duplicate(e, x=i*20)
# e.model.set_render_mode_perspective(True)
# print(t.pixels)
# for row in t.pixels:
#     for c in row:
#         print((c[0] + c[1] + c[2]) / 3)
t = 0
# def update():
#     global t
#     t += time.dt
#     if t < .1:
#         return
#     t = 0
#     e.model.vertices = [v+Vec3(.05,0,0) for v in e.model.vertices]
#     e.model.generate()






app.run()
