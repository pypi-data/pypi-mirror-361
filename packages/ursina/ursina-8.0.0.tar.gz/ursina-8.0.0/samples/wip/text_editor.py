### tree view ###
from ursina import *
from pathlib import Path


class TreeView(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, position=window.top_left)
        Text.size = 1/window.size[1]*14
        Text.default_font = 'arial.ttf'
        Text.default_resolution = 14*2
        # self.font = 'arial.ttf'

        self.line_height = 1.5
        self.button_size = (.3, Text.size * self.line_height)
        self.y -= self.button_size[1]

        self.bg = Panel(parent=self, model='quad', origin=(-.5,.5), scale=(self.button_size[0],1), color=color._15, z=1)
        self.path = Path('.')
        self.opened_dirs = list()
        self.opened_dirs.append(self.path / 'Models')
        self.opened_dirs.append(self.path / 'Models' / 'compressed')
        # do this to draw text once for the whole tree view instead of for every button
        self.text = ''
        self.text_entity = Text(parent=self, z=-1, line_height=self.line_height)
        self.text_entity.world_y -= (self.button_size[1] * 20) + self.button_size[1] * 5

        self.top_bar = Button(
            text = ' <gray>* ' + str(self.path.resolve()),
            model = 'quad',
            color = color._30,
            scale = (camera.aspect_ratio, self.button_size[1]),
            text_origin = (-.5,0),
            origin = (-.5, .5),
            pressed_scale = 1,
            position = window.top_left
            )

        self.draw_tree()


    def draw_folder(self, folder):
        # global text
        arrow = '> '
        if folder in self.opened_dirs:
            arrow = 'v '

        # print('    '*str(folder).count('\\') + arrow + folder.name)
        self.text += ' <white>'+'  '*str(folder).count('\\') + arrow + folder.name + '\n'
        b = Button(
            parent = self,
            model = 'quad',
            scale = self.button_size,
            pressed_scale = 1
            )

        def folder_button_click():
            if not folder in self.opened_dirs:
                self.opened_dirs.append(folder)
            else:
                self.opened_dirs.remove(folder)
            self.draw_tree()

        b.on_click = folder_button_click


        if folder in self.opened_dirs:
            for subfolder in [e for e in folder.glob('*') if e.is_dir()]:
                self.draw_folder(subfolder)

            for file in [e for e in folder.glob('*') if e.is_file()]:
                self.text += ' <gray>' + '  '*str(file).count('\\') + file.name + '\n<default>'
                b = Button(
                    parent = self,
                    model = 'quad',
                    scale = self.button_size,
                    pressed_scale = 1
                    )


    def draw_tree(self):
        t = time.time()
        self.text = ''
        [destroy(e) for e in self.children if not e in (self.bg, self.text_entity)]

        self.project_button = Button(
            parent = self,
            text = ' ' + self.path.resolve().name,
            model = 'quad',
            color = color.yellow.tint(-.5),
            scale = self.button_size,
            text_origin = (-.5, 0),
            pressed_scale = 1,
            )

        for folder in [e for e in self.path.glob('*') if e.is_dir()]:
            self.draw_folder(folder)

        for i, e in enumerate([e for e in self.children if not e in (self.bg, self.text_entity)]):
            e.origin = (-.5, .5)
            e.y = -i*self.button_size[1]

        self.text_entity.text = self.text
        print('drew file tree:', time.time() - t)




if __name__ == '__main__':
    app = Ursina()

    TreeView()

    Button.color = color._20
    window.color = color._25
    window.size /= .75
    window.x = 200
    app.run()
