from ursina import *
from tinyblend import BlenderFile


def load_level(name, path=application.asset_folder):
    if not name.endswith('.blend'):
        name += '.blend'

    files = list(path.glob(f'**/{name}'))
    print('files:', files)
    if not files:
        print(f'error: level {name} not found')
        return

    blend_file = files[0]
    # import bpy
    # dir(bpy.data)
    #
    with open(blend_file, 'rb') as f:
        blender_version_number = (f.read(12).decode("utf-8"))[-3:]   # get version from start of .blend file e.g. 'BLENDER-v280'
        blender_version_number = blender_version_number[0] + '.' + blender_version_number[1:2]
        print('blender_version:', blender_version_number)
        if blender_version_number in application.blender_paths:
            blender = application.blender_paths[blender_version_number]
        else:
            print('using default blender version')
            blender = application.blender_paths['default']

    a = subprocess.check_output(f'''"{blender}" "{blend_file}" --background --python {application.asset_folder/'blender_scene_parsing_script.py'}''', shell=True)
    a = a.decode( "utf-8")
    print('a:', a)
    # blend = BlenderFile(file)
    # structs = blend.list('Object')
    # # structs = blend.data
    # for o in structs:
    #     # print(e.collection)
    #     object_name = o.id.name.decode( "utf-8").replace(".", "_")[2:]
    #     object_name = object_name.split('\0', 1)[0]
    #     print('name:', object_name)

if __name__ == '__main__':
    load_level('blender_level_editor_test_scene')
