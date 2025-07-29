# from ursina import *
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
# loadPrcFileData('', 'coordinate-system y-up-left')

# app = Ursina()
app = ShowBase()
# app.disableMouse()
# Sky()

pandaActor = Actor('Player.bam')
pandaActor.reparentTo(base.render)
# EditorCamera()
pandaActor.loop('Running')
pandaActor.setPos(0,15,0)
# pandaActor.setPos(0,0,15)
# camera.y = 20
app.run()
