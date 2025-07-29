if __name__ == '__main__':
    from ursina import *


    app = Ursina()

    face_parent = Entity(texture='sliced_cube_template')
    # middle = Entity(parent=face_parent, model='quad', scale=.5, texture='sliced_cube_template', texture_scale=Vec2(.5), texture_offset=Vec2(.25))
    #
    # for corner in [e/2 for e in [Vec2(1,1), Vec2(1,-1), Vec2(-1,-1), Vec2(-1,1)]]:
    #     print(corner)
    #     Entity(parent=face_parent, model='quad', origin=corner, position=corner, scale=.25, texture='sliced_cube_template', texture_scale=Vec2(.25), texture_offset=(corner+Vec2(.5))*.75)
    #
    # for side in [e/2 for e in [Vec2(0,1), Vec2(1,0), Vec2(0,-1), Vec2(-1,0)]]:
    #     Entity(parent=face_parent, model='quad', origin=side, position=side, scale=Vec2(.25,.25)+abs(side.yx), texture='sliced_cube_template', texture_scale=Vec2(.25,.8), texture_offset=(0,0), color=color.white)


    # face_parent.combine()
    quad = load_model('quad', use_deepcopy=True)

    vertices = []
    uvs = []

    vertices.extend([v/2 for v in quad.vertices])
    uvs.extend([(uv/2)+Vec2(1/4) for uv in quad.uvs])

    for corner in [e/2 for e in [Vec2(1,1), Vec2(1,-1), Vec2(-1,-1), Vec2(-1,1)]]:
        vertices.extend([(v/4) + corner*.75 for v in quad.vertices])
        uvs.extend([(uv/4)+(corner+Vec2(.5))*.75 for uv in quad.uvs])

    # for side in [e/2 for e in [Vec2(0,1), Vec2(1,0), Vec2(0,-1), Vec2(-1,0)]]:
    #     vertices.extend([(v*Vec3(*abs(side.yx))) + side.yx + Vec3(0,0,-.5)for v in quad.vertices])
    #     uvs.extend([(uv/4)+(side+Vec2(.5))*.75 for uv in quad.uvs])
    #     # tris.append([i for i in range(len(vertices), len(vertices)+4)])
    #     # Entity(parent=face_parent, model='quad', position=side*.75, scale=Vec2(.25,.25)+abs(side.yx), texture='sliced_cube_template', texture_scale=Vec2(.25,.8), texture_offset=(0,.1), color=color.white)

    for side, uv_offset in zip([e/2 for e in [Vec2(0,1), Vec2(1,0), Vec2(0,-1), Vec2(-1,0)]], [Vec2(.25,0), Vec2(.75,.25), Vec2(.25,.75), Vec2(0,.25)]):
        size = Vec3(.25,.25, 1) + (abs(side.yx)*.5)
        position = (Vec3(*side,0) * .75)

        vertices.extend([(v * size) + position for v in quad.vertices])
        uvs.extend([(uv*size) + uv_offset for uv in quad.uvs])

    m = Mesh(vertices=vertices,  uvs=uvs)
    Entity(model=m, texture='sliced_cube_template')


    Entity(model='wireframe_quad', color=color.green, alpha=.5)
    # Entity(model=m, texture='shore')
    EditorCamera()
    app.run()
