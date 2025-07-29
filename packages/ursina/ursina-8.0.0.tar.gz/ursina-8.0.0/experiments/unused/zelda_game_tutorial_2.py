from ursina import *

app = Ursina()


player = Entity(model='cube', color=color.azure, origin_y=-.5)
player.speed = 3
ground = Entity(model='plane', scale=8, color=color.lime, texture='white_cube', texture_scale=(8,8))


camera.position = (4,8,-16)
camera.look_at((0,0,0))


def update():
    player.z += held_keys['w'] * time.dt
    player.z -= held_keys['s'] * time.dt
    player.x += held_keys['d'] * time.dt
    player.x -= held_keys['a'] * time.dt


app.run()
