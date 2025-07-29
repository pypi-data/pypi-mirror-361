from ursina import *



app = Ursina()

window.color=color.black
e1 = Entity(model='plane', scale=10, collider='box', color=color.dark_gray)
e2 = Entity(model='cube', collider='box', color=color.dark_gray)

# sun = Entity(model='sphere', scale=.05, color=color.yellow, add_to_scene_entities=False)
camera.orthographic = True
ed = EditorCamera()


def input(key):
    if key == 'left mouse down':
        print('generate shadows')
        # for e in (e1, e2):
            # Entity(model='plane', world_scale=.05, parent=e, )
        # e = Entity(model='plane', scale=.05, position=mouse.world_point)
        m = Entity(model=Mesh(mode='point', thickness=.1))
        for y in range(64):
            for x in range(64):
                ray = raycast(camera.world_position + Vec2(x/4,y/4), camera.forward)
                print(ray.hit)
                if ray.hit:
                    m.model.vertices.append(ray.world_point)
                    # e = Entity(model='plane', scale=.2, position=ray.world_point)
                    # e.look_at(camera, 'up')

        m.model.set_render_mode_perspective(True)
        m.model.generate()






app.run()
