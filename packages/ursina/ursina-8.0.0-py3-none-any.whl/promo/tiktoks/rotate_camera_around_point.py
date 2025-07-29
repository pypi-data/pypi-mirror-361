# how to move rotate the
# camera around a point.

from ursina import *
from ursina.shaders import lit_with_shadows_shader #!hide
Entity.default_shader = lit_with_shadows_shader #!hide

app = Ursina()
window.size = Vec2(1080, 1920) * .5 #!hide
window.position = (0,0) #!hide

# Make an empty Entity to help
# us rotate.
origin = Entity()

# Parent the camera to the entity.
camera.parent = origin

# Move the camera back.
camera.z = -20

# Rotate when we right click and
# drag.
def update():
  origin.rotation_y += (
    # How far the mouse moved
    # horizontally since last
    # update.
    mouse.velocity[0]
    # Only rotate if right
    # mouse button is being
    # held.
    * mouse.right * 100
    )
  # Do the same vertically.
  origin.rotation_x -= (
    mouse.velocity[1]
    * mouse.right * 100
    )

# Create a cube on some grass
# so we have something to
# look at :D
player = Entity(
  model='cube',
  origin_y=-.5,
  color=color.orange
  )
grass = Entity(
  model='plane',
  scale=40,
  texture='grass',
  texture_scale=Vec2(10)
  )
DirectionalLight().look_at(Vec3(.5,-1,.5)) #!hide
Sky() #!hide
# Run program!
app.run()
