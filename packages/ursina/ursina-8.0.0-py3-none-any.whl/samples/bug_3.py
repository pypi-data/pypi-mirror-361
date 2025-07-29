from ursina import *
app = Ursina()
a = Audio('sine.wav',loop=True)
print(a.length)
def input(key):
    if key=='space':
        if a.playing:
            a.pause()
            print('pause')
        else:
            a.resume()
            print('resume')
app.run()