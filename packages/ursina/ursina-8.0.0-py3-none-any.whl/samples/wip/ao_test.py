from ursina import *


# window.size = (128,128)
app = Ursina()
#
p = Entity()
# Entity(parent=p, model='plane', color=color.gray, scale=50)
Entity(parent=p, model='procedural_rock_0', color=color.dark_gray, scale=2, rotation_z=-45, y=1)
# Entity(parent=p, model='sphere', color=color.dark_gray, scale=4, rotation_z=-45, y=2)
Entity(model='plane', color=color.yellow.tint(-.3), scale=50)


p.combine()
side_color = color.color(44,.43,.26)
p.model.colorize(
    side_color, side_color,
    side_color.tint(-.2), color.gray,
    side_color, side_color,
    smooth=False)
# # p.model.calculate_normals()
# # print(p.bounds)
# # bounds = [int(e) for e in p.bounds]
# # voxels = list()
# #
# # rounded_verts = [(int(v[0]), int(v[1]), int(v[2])) for v in p.model.vertices]
# # print(rounded_verts)
# # for y in range(bounds[1]):
# #     for z in range(bounds[2]):
# #         for x in range(bounds[0]):
# #             if not (x,y,z) in rounded_verts:
# #                 continue
# #
# #             e = Entity(model='cube', origin=(-.5,-.5,-.5), color=color.random_color(), position=(x,y,z))
# #
# #             voxels.append(e)
# seq = Sequence()
# # target = Entity(model='quad', scale=.1, color=color.lime)
# target = camera
#
# new_colors = list()
#
# for i, v in enumerate(p.model.vertices):
#     seq.append(Func(setattr, target, 'position', Vec3(*v)-(Vec3(*p.model.normals[i])*.05)))
#     seq.append(Func(target.look_at, Vec3(*v)+p.model.normals[i]))
#     # seq.append(Wait(.01))
#     # seq.append(Func(app.graphicsEngine.renderFrame))
#
#
# seq.append(Func(EditorCamera))
#
#
# def input(key):
#     if key == 'b':
#         seq.start()
#
#
# # Sky()
# sun = Entity(model='sphere', color=color.yellow, position=(10,100,30), scale=30)
#
#
# # def capture():
#     # t = base.screenshot()
#     # print(t.get_pixel(0,0))
#
#
#     # from panda3d.core import Shader
#     # from direct.filter.FilterManager import FilterManager
#     # # manager = FilterManager(base.win, base.cam)
#     # manager = FilterManager(base.win, camera.ui_camera)
#     # from panda3d.core import Texture as PandaTexture
#     # tex = PandaTexture()
#     # quad = manager.renderSceneInto(colortex=tex)
#     # # quad.setShader(Shader.load("contrast.sha"))
#     # quad.setShaderInput("tex", tex)
#     # # quad.setShaderInput("contrast", 1.0)
# altBuffer = app.win.makeTextureBuffer("hello", 256, 256)
# app.makeCamera(altBuffer)
# Entity(model='quad', texture=altBuffer.getTexture())
#
# window.center_on_screen()
# # p.color = color.black
# # window.color = color.black
# # invoke(capture, delay=1)
EditorCamera()
app.run()
