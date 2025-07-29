from ursina import *
from direct.actor.Actor import Actor

if __name__ == '__main__':
    app = Ursina()

    # application.asset_folder = Path('/home/poke/Downloads/')

    Actor('rn.glb')

    EditorCamera()
    app.run()