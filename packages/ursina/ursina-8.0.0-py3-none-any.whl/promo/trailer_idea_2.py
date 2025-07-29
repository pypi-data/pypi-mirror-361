from ursina import *
from cool_scene_transition import CoolSceneTransition



app = Ursina(forced_aspect_ratio=16/9)


def swooshy_text(text, background_color=color.black, scale=1.5):
    pivot = Entity()
    # pivot = Entity(world_parent=camera.ui)
    t = Text(parent=pivot, z=-10, text=text, scale=20, origin=(0,0), background=True)
    t.create_background(padding=(1,.5), radius=.01, color=background_color)

    pivot.rotation_y = -45
    pivot.animate_rotation_y(0, duration=1*scale, curve=curve.in_out_expo)
    pivot.animate_rotation_y(45, duration=1*scale, delay=1.3*scale, curve=curve.in_out_expo)
    t.color = color.clear
    t.animate_color(color.smoke, duration=.5*scale)
    t.animate_color(color.clear, duration=.5*scale, delay=1.3*scale)
    t.background.color = color.clear
    t.background.animate_color(background_color, duration=.5*scale)
    t.background.animate_color(color.clear, duration=.5*scale, delay=1.3*scale)
    t.x = 1
    t.animate_x(-1, duration=2*scale, curve=curve.linear)
    destroy(pivot, delay=2*scale)


# window.fullscreen = True
ursina_green = color.color(122, .57, .69).tint(-.15)
ursina_green = color.azure.tint(0)
import trailer_code_example
window.color = color.black
Text.default_resolution *= 2
Text.default_font = 'VeraMono.ttf'
Texture.default_filtering = 'bilinear'
step = 8.72/8

intro_text = Text("A new <lime>game engine<default> has entered the arena!", origin=(0,0), scale=2, enabled=False)
music = Audio('Reloaded Installer _3.mp3', autoplay=False)

logo = Sprite(name='ursina_splash', parent=camera.ui, texture='ursina_logo', world_z=camera.overlay.z-1, scale=.12, color=color.clear)
bg = Entity(model=Cylinder(16, mode='line', thickness=1), color=color.azure, scale=80, scale_y=16, x=-20, y=-5, enabled=False)
inner_wall = Entity(parent=bg, model=Cylinder(16, mode='line', thickness=1), scale=.25, scale_y=1, color=bg.color)

trailer_code_example.tf.x -= .2

video_parent = Entity(parent=camera.ui, x=-.5*camera.aspect_ratio)
video_parent.world_parent = scene
video_parent.original_position = video_parent.position
video_parent.rotate = True
video_parent.rotation_speed = .01

def reset():
    video_parent.position = video_parent.original_position
    video_parent.rotation_y = 0
video_parent.reset = reset

class Video(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui, model='quad', scale_x=camera.aspect_ratio, world_parent=video_parent, enabled=False)

        for key, value in kwargs.items():
            setattr(self, key, value)



one_gameplay =        Video(texture='one_gameplay.mp4')
inventory_gameplay =  Video(texture='inventory_example_gameplay.mp4')
value_of_life =       Video(texture='value_of_life_gameplay.mp4')

voxel_tool =          Video(texture='voxel_tool_gameplay_cut.mp4', position=(.4,-.2))
voxel_tool.scale *= .5
voxel_tool.x = 1.4

hotreloading =        Video(texture='code_hotreloading.mp4')
hotreloading.scale *= 1.05

cool_scene_transition = CoolSceneTransition()
loddefjord = Video(texture='loddefjord.mp4')
# loddefjord.texture.set_play_rate(1.4)
loddefjord.texture.set_play_rate(.85)
loddefjord.texture.stop()

column_graph = Video(texture='column_graph.mp4')
column_graph.texture.set_play_rate(2.9)

mysterious_sphere = Video(texture='mysterious_sphere.mp4')
mysterious_sphere.texture.stop()

autoblock_footage = Video(texture='autoblock_footage.mp4')
autoblock_footage.texture.set_play_rate(3)

# tunnel = Entity(model=Prismatoid(base_shape=Circle(12), path=[Vec3(0,0,i*2) for i in range(8)],mode='line'), scale=10, color=color.azure.tint(-.2), z=-12, enabled=False)
download_text = Text("Get started now!", origin=(0,0), scale=1.5, enabled=False, y=.1)
link =          Text("www.ursinaengine.org", origin=(0,0), scale=2, enabled=False, y=-.0)
music_credit =  Text("Music by LHS", origin=(0,-.5), scale=1, enabled=False, y=-.47)

for movie in (loddefjord, column_graph, mysterious_sphere, autoblock_footage):
    movie.scale *= 1.125
    movie.texture.stop()

for movie in (inventory_gameplay, value_of_life, voxel_tool):
    movie.texture.stop()
    movie.texture.set_loop_count(1)


cumulative_time = 25.29750

s = Sequence(
    Func(music.play),
    Func(setattr, bg, 'enabled', True),
    Func(setattr, intro_text, 'enabled', True), Func(intro_text.appear, speed=.05),
    Wait(step*2),
    Func(intro_text.fade_out),
    Wait(step*.5),

    Func(logo.animate_color, color.white, duration=step),
    Func(logo.animate_scale, logo.scale*1.25, curve=curve.linear, duration=step*8),
    Wait(step*5),
    Func(logo.animate_color, color.clear, curve=curve.linear, duration=step),
    Wait(step*1),

    Func(camera.overlay.blink, color.black, duration=1),
    Wait(.5),
    Func(swooshy_text, "Make Games", background_color=ursina_green),
    Func(setattr, bg, 'enabled', False), Func(video_parent.reset),

    Func(one_gameplay.texture.play), Func(setattr, one_gameplay, 'enabled', True), Wait(step*2.75), Func(setattr, one_gameplay, 'enabled', False), Func(video_parent.reset),
    Func(inventory_gameplay.texture.play), Func(setattr, inventory_gameplay, 'enabled', True), Wait(step*2.25), Func(setattr, inventory_gameplay, 'enabled', False),Func(video_parent.reset),
    Func(setattr, value_of_life, 'enabled', True), Func(value_of_life.texture.play), Wait(step*2.25), Func(setattr, value_of_life, 'enabled', False),

    Func(swooshy_text, "Code in Python", background_color=ursina_green),
    step*2,
    Func(trailer_code_example.tf.text_entity.appear, speed=.0025),
    Func(video_parent.reset),
    Func(setattr, voxel_tool, 'enabled', True), Func(voxel_tool.texture.play),
    step*4,
    Func(camera.overlay.blink, color.black, duration=step),
    step/2,
    Func(setattr, trailer_code_example.tf, 'text', ''),
    Func(trailer_code_example.tf.render),
    Func(setattr, voxel_tool, 'enabled', False),
    Func(setattr, trailer_code_example, 'enabled', False),
    step/2,


    # Func(music.play, cumulative_time),

    Func(setattr, video_parent, 'position', video_parent.original_position), Func(setattr, video_parent, 'rotation_y', 0),

    Func(swooshy_text, "Low Friction Workflow", background_color=ursina_green),
    Func(hotreloading.texture.play), Func(setattr, hotreloading, 'enabled', True),
    Wait(step*5.5),
    Func(cool_scene_transition.play, .9),
    Wait(step*1),
    Func(setattr, hotreloading, 'enabled', False),
    Func(video_parent.reset),
    Func(setattr, video_parent, 'rotate', False),

    Func(setattr, loddefjord, 'enabled', True), Wait(.8),
    Func(swooshy_text, "Free and Open Source", background_color=ursina_green),
    Func(loddefjord.texture.play), Wait(5.5), Func(setattr, loddefjord, 'enabled', False),
    # Func(swooshy_text, "Modern UI", background_color=ursina_green),
    Func(setattr, column_graph, 'enabled', True), Func(column_graph.texture.play), Wait(step*4.7), Func(setattr, column_graph, 'enabled', False),
    Func(setattr, mysterious_sphere, 'enabled', True), Func(mysterious_sphere.texture.play), Wait(step*2.5), Func(setattr, mysterious_sphere, 'enabled', False),
    # Func(swooshy_text, "Procedural Geometry", background_color=ursina_green),
    Func(autoblock_footage.texture.play), Func(setattr, autoblock_footage, 'enabled', True), Wait(7.5),
    Func(camera.overlay.blink, color.black, duration=1), Wait(.5), Func(setattr, autoblock_footage, 'enabled', False),

    Func(setattr, window, 'color', color.color(122, .57, .69).tint(-.3)),
    Func(setattr, download_text, 'enabled', True), Func(download_text.appear, speed=.1),
    2,
    Func(download_text.fade_out, duration=3),
    Func(setattr, link, 'enabled', True), Func(link.appear, speed=.1),
    Func(link.animate_scale, link.scale*1.5, curve=curve.linear, duration=step*8),
    5,
    Func(setattr, music_credit, 'enabled', True),
    Func(setattr, music_credit, 'color', color.clear),
    Func(music_credit.animate_color, color.white, duration=3),
    Func(music.fade_out, duration=8),
)
# window.color = color.lime.tint(-.5)
# window.color = color.color(122, .57, .69).tint(-.3)
window.editor_ui.enabled = False

started = False

def update():

    if started:
        bg.rotation_y += 1
        bg.rotation_x -= .05

        if video_parent.rotate:
            video_parent.rotation_y += video_parent.rotation_speed
            video_parent.x -= .005
        # if tunnel.enabled:
        #     tunnel.z -= .15

def input(key):
    global started

    if not started and key == 'space':
        s.start()
        started = True
        print('start')

camera.fov = 90


app.run()
