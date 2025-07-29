from ursina import *

class Player(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'play'
        self.model = 'quad'

        # adds a Weapon instance to self.scripts and andds self.weapon
        # self gets added to weapon instance as 'entity'
        # self.add_script(Weapon()) # instance
        # self.add_script('weapon') # module name
        # self.add_script('Weapon') # class name
        # printvar(self.weapon)
        # self.weapon = Weapon()
        # print(self.weapon)

    def attack(self):
        print('ATTACK!')


    def input(self, key):
        if key == 'd':
            destroy(self.weapon)

class Weapon():
    def __init__(self):
        self.damage = 10

    def input(self, key):
        if key == 'e':
            self.entity.animate_color(color.yellow, duration=.5)
            self.entity.animate_color(color.white, delay=2, duration=1.5)
            self.entity.attack()

class Tester(Entity):
    def __init__(self):
        super().__init__()

    def input(self, key):
        if key == 't':
            print('t')
            pass
            # print(len(globals()))
            # print(app.player.weapon)
            # for g in globals():
            #     print(g)
                # try:
                #     print(g.name)
                # except:
                #     pass


app = Ursina()
t = Tester()
app.player = Player()
app.run()
