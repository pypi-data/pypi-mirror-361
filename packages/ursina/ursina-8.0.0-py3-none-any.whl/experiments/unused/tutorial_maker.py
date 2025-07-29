from ursina import *


app = Ursina()

steps = [
'''
a




''',

]

t = Text(font='VeraMono.ttf', origin=(-.5,.5))




app.run()


'''
installation
basics / overview
cheat sheet
tutorials
example projects
faq
how to create a build

'''
The Entity god class

Most things are entities. The camera, a Button, Text, they all inherit from Entity.
This class



The Camera




Working with the Button class

Creating a button
b = Button()

Transforming the button
Since Button inherits Entity, we can transform in the same way:
b.position = (-.5, 0)
b.scale = .2

The 'origin' attribute can be very useful for ui elements.
By default it's in the center of the button, (0,0):
-------
|  *  |
-------

b.origin = (-.5, .5) # move the origin to the top left
*------
|     |
-------





There multiple way to define what happen when we click on a Button.
In any case we'd have to set the on_click attribute.

def button_click():
    print('click')

b.on_click = button_click # assign a method

b.on_click = Func(print, 'click') # assign a Func. This will call print with the argument 'click'

b.on_click = Sequence(Wait(1), Func(print, 'click delayed'))
