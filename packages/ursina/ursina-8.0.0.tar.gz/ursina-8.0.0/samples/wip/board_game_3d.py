from ursina import *
from ursina.shaders import basic_lighting_shader
window.vsync = False

app = Ursina()

window.color=color.smoke
board = Entity(model='plane', scale=8, texture='white_cube', texture_scale=(8,8), origin=(-.5,0,-.5))

# make a pawn model by using a procedural Pipe
pawn_model = Pipe(
    base_shape=Circle(16),
    path=[Vec3(0,y,0) for y in [.05, .063, .1, .146, .173, .21, .254, .275, .288, .434, .445, .5, .556, .618, .7, .778, .85, .9, .92]],
    thicknesses=(.632, .58, .64, .64, .56, .4, .384, .350, .25, .230, .4, .45, .2, .35, .43, .434, .38, .26, 0)
    )
pawn_model.generate_normals()


# create pawns
for i in range(8):
    piece = Draggable(
        parent=scene,   # set to scene so it's not on the "ui layer"
        model=copy(pawn_model),   # set the model we create earlier
        color=color.smoke,
        highlight_color=color.lime,
        origin=(-.5,0,-.5),     # offset the model
        plane_direction=(0,1,0),    # make the plane it moves along point upwards
        step=(1,1,1),
        shader=basic_lighting_shader,
        x=i,
        z=1,
        )
    piece.set_shader_input('transform_matrix', piece.getNetTransform().getMat())

    # assign a drop function to the piece which will be called when release the mouse
    def drop():
        piece.position = round(piece.position, 0)
    piece.drop = drop


Cursor()
mouse.visible = False
Sky(texture='sky_sunset')
Entity(model='plane', color=color.light_gray, scale=2000, y=-.01, texture='grass', texture_scale=(100,100))
EditorCamera(rotation_x=30, position=(4,0,4))



app.run()
