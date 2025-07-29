from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

application.asset_folder = application.asset_folder.parent
app = Ursina()

Entity(
    model='mysterious_sphere',
    texture='mysterious_sphere_ao_map',
    collider='mesh'
    )

Sky()
player = FirstPersonController()
player.cursor.enabled = False
player.speed *= .5
window.exit_button.visible = False
# window.fps_counter.enabled = False

# Entity(model='plane', scale=1000, color=color.azure)
sun = Entity(y=10, z=1000)

Entity(model='sphere', y=2, z=-8, color=color.red, scale=3)


# from direct.filter.CommonFilters import CommonFilters
# filters = CommonFilters(base.win, base.cam)
#
# filters.setAmbientOcclusion()
# filters.setVolumetricLighting(sun)


app.run()
