from ursina import *
# import tripy


app = Ursina()
window.borderless = False
camera.orthographic = True
window.color=color.black

verts = Circle(3).vertices
verts = [v*Vec3(2,1,1) for v in verts]
shape = Entity(model=Mesh(vertices=verts, triangles=(0,1,2), mode='triangle'), scale=10, texture='brick')
dummy = Entity()
# cursor = Draggable(model='sphere', color=color.azure, scale=.02, step=0, name='cursor')
point_renderer = Entity(parent=shape, model=Mesh(mode='point', thickness=.02), color=color.white, texture='circle', always_on_top=True)
point_renderer.model.set_render_mode_perspective(True)
target_index = -1

shape.cursor_parent = Entity(parent=shape, cursor_index=-1)

m = Entity(parent=shape, model=Mesh(mode='triangle', thickness=10)).model
helper = Entity()
offsetter = Entity(parent=helper, model='quad', scale=.01, y=.2)


def input(key):
    # global target_index
    # if not mouse.hovered_entity:



    # if not shape.edit_mode:
    #     return

    target = mouse.hovered_entity
    if target and target.model:
        target.color = color.yellow

    if key == 'left mouse down':
        # cursor.enabled = False
        dummy.parent = shape
        # cursor.world_parent = scene

        for i, v in enumerate(shape.model.vertices):
            dummy.position = v
            # print(distance(mouse.position, dummy.screen_position))
            if distance(mouse.position, dummy.screen_position) < .025:
                print('-------------')
                # cursor.parent = shape
                # cursor.enabled = True
                # cursor.position = v
                # cursor.parent = scene
                # cursor.world_scale = 1
                # cursor.target_index = i
                target_index = i
                # mouse.position = dummy.screen_position
                # cursor.dragging = True
                # invoke(setattr, cursor, 'dragging', True, delay=.1)
                break



    if key == 'n':
        cursor_index = shape.cursor_parent.cursor_index
        print('----------', cursor_index)
        if cursor_index < 0:
            return
        next_index = cursor_index + 1
        if next_index >= len(shape.model.vertices):
            next_index = 0

        new_vert = lerp(shape.model.vertices[cursor_index], shape.model.vertices[next_index], .5)
        new_vert += Vec3(.1,0,0)

        if cursor_index == len(shape.model.vertices)-1:
            shape.model.vertices.append(new_vert)
        else:
            pass
            shape.model.vertices.insert(next_index, new_vert)

        # cursor.position = new_vert
        update_shape()


    if key == 'delete' and cursor.enabled and len(shape.model.vertices) > 3:
        shape.model.vertices.pop(cursor.target_index)
        shape.model.generate()



    # draw_numbers()


def update_shape():
    from panda3d.core import Triangulator, LPoint2d
    triangulator = Triangulator()
    shape.model.vertices = [Vec3(e.x,e.y,e.z) for e in [Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,-.25), Vec3(.75,0,-.25), Vec3(.75,0,.25), Vec3(.5,0,.25), Vec3(.5,0,.5), Vec3(.5,0,.55), Vec3(-.5,0,.5)]]
    for v in shape.model.vertices:
        vi = triangulator.add_vertex(v[0], v[2])
        triangulator.addPolygonVertex(vi)

    triangulator.triangulate()

    shape.model.triangles = list()

    for i in range(triangulator.getNumTriangles()):
        shape.model.triangles.extend((
            triangulator.getTriangleV0(i),
            triangulator.getTriangleV1(i),
            triangulator.getTriangleV2(i),
        ))

    shape.model.uvs = [v*10 for v in shape.model.vertices]
    shape.model.generate()

    # shape.collider = 'mesh'

    point_renderer.model.vertices = copy(shape.model.vertices)
    point_renderer.model.generate()



    for e in shape.cursor_parent.children:
        destroy(e)

    for i, v in enumerate(shape.model.vertices):
        print('dddd', i)
        cursor = Draggable(parent=shape.cursor_parent, position=v, text=f'<blue>{i}', world_scale=1, color=color.white33, always_on_top=True)
        cursor.target_index = i

        def drag(i=i):
            shape.cursor_parent.cursor_index = i
        cursor.drag = drag

        def drop(cursor=cursor):
            print('drop')
            # shape.model.vertices[cursor.target_index] = cursor.position
            cursor.world_parent = shape.cursor_parent
            shape.model.vertices[cursor.target_index] = cursor.position

            update_shape()

        cursor.drop = drop



    verts = copy(shape.model.vertices)
    verts.append(shape.model.vertices[0])
    m.vertices.clear()
    m.triangles.clear()
    j = 0
    for _i, v in enumerate(verts):
        if _i == len(verts)-1:
            next_point = verts[0]
        else:
            next_point = verts[_i+1]

        if _i == 0:
            prev_point = verts[len(verts)-1]
        else:
            prev_point = verts[_i-1]

        # helper.parent = shape
        # helper.position = v
        # helper.look_at_2d(prev_point)
        # a = helper.rotation_z
        # helper.look_at_2d(next_point)
        # b = helper.rotation_z
        # # if a < 0:
        # #     a = 360 + a
        # # if b < 0:
        # #     b = 360 + b
        #
        # helper.rotation_z = lerp(a, b, .5)
        #
        # helper.rotation_z = (a + b) / 2
        # # helper.position = (prev_point + next_point) / 2
        # # look_at_point = helper.world_position
        # # # helper.look_at_2d((prev_point + next_point) / 2)
        # # helper.position = v
        # # helper.look_at_2d(look_at_point)
        #
        # Entity(parent=shape.cursor_parent, model='cube', origin_y=-.5, scale_x=.05, scale_z=1, color=color.red, scale_y=.5, rotation_z=helper.rotation_z, position=helper.position)
        # Entity(parent=shape.cursor_parent, model='cube', scale=.05, scale_z=1, position=lerp(v, prev_point, .1), color=color.lime)
        # Entity(parent=shape.cursor_parent, model='cube', scale=.05, scale_z=1, position=lerp(v, next_point, .1), color=color.orange)
        # m.vertices.append(helper.position)
        # m.vertices.append(offsetter.get_position(shape))
        #
        # if _i > 0:
        #     print([e+j for e in (0,1,2,3)])
        #     m.triangles.append([e+j for e in (2,1,0)])
        #     m.triangles.append([e+j for e in (1,2,3)])
        #
        #     j+=2

    m.generate()
    print('...............')










texts = list()
def draw_numbers():
    global texts
    for t in texts:
        destroy(t)

    for i, v in enumerate(shape.model.vertices):
        t = Text(text=i, world_parent=shape, position=v, z=-.1)
        t.scale *= 2
        texts.append(t)

# draw_numbers()
# def set_edit_mode(value):
#     point_renderer.enabled = value
#     cursor.enabled = value
# def update():
#     print(mouse.hovered_entity)

EditorCamera()
# cursor.drop = drop
update_shape()



app.run()
