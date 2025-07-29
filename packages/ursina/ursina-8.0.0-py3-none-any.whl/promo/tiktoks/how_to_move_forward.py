# How to move forward while
# taking rotation into account

from ursina import *
from ursina.shaders import lit_with_shadows_shader #!hide
Entity.default_shader = lit_with_shadows_shader #!hide

app = Ursina()
window.size = Vec2(1080, 1920) * .5 #!hide
window.position = (0,0) #!hide

# Make an Entity for the car
car = Entity(
  model='car',
  color=color.red,
  z=-3,
  speed=8
  )
car.model.save('car.bam')

# Make the car rotate
def update():
  car.rotation_y += (
    (held_keys['d']-held_keys['a'])
# Multiply with time.dt to make
# it framerate independent
    * time.dt
# It's a little slow, so let's
# multiply it by 100
    * 100
    )

# Changing car.z won't
# take rotation into account.
# Do this instead:
  car.position += (
# Get the input.
# w to move forward,
# s to move backward
    (held_keys['w']-held_keys['s'])
    * car.speed * time.dt
# Get forward vector with .forward
# Facing straight: Vec3(0,0,1).
# Facing right: Vec3(1,0,0).
# And so on.
    * car.forward
    )

Entity(model='plane', scale=40, texture='grass', texture_scale=Vec2(5)) #!hide
camera.z = -15 #!hide
EditorCamera(rotation=(30,-10,0)) #!hide
DirectionalLight().look_at(Vec3(.5,-1,.25)) #!hide
Sky() #!hide
# Run
app.run()
