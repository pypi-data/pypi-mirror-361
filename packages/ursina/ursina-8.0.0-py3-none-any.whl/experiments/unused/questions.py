Altering a 3d model
To change a model, just change it's attributes like .vertices, .triangles, .colors, .uvs, .normals, or .mode.
e = Entity(model='cube')

# move vertices above the origin up 1, to make a capsule
for v in e.model.vertices:
    if v.y > 0:
        v.y += 1

e.model.generate() # call this to update the mesh

You can also create a Mesh by scratch if you want that.
If you set model.mode = 'line' and call model.generate() it will render it as lines, but
keep in mind it might not look exactly as expected it if it's mean to be solid.

To set window display_mode
window.display_mode = 'wireframe' # render everything as wireframe

You can also press F10 to toggle between default, wireframe, colliders, normals. F9 to return to default.


UV Scrolling
Modifying a Mesh instance and regenerating it every frame is not the best way to make texture scrolling, however.
It's too expensive to do that every frame so you can set 'texture_offset' and 'texture_scale' instead. I noticed they're not
listed in the API reference and had actully forgotten about them myself. :P


Lighting
Lights are not really supported at the moment. The reflectivity is a work in progress as well, since I couldn't get it work like I wanted.
You can however take a look at panda3d's documentation and use the lights from there if you'd like.
Since ursina is made on top of panda3d you can always fall back to that control things at a lower level.

There's a really basic shader called 'basic_lighting' you can use of you just want to see the shape of the model better. No cast shadows included, but at least it's not flat shaded.
Or you could set window.display_mode = 'normals'. Keep in mind the model needs normals for these to work.
If the model doesn't have them you can generate them with entity.model.generate_normals(). It can take whole to do that though, especially for bigger meshes.

Often in games it's a good idea to bake the shadows anyway, as real-time shadows tend to multiply the draw calls.
