from ursina import *

app = Ursina()

t = time.time()
a = Animation('blob_animation', fps=24)
# for f in a.frames:
#     f.model.save(f.model.path.stem + '.bam')
print('----', time.time() - t)
app.run()
