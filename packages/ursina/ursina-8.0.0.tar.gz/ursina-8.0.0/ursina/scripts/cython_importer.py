import importlib
import importlib.util
import sys
from pathlib import Path
from ursina.string_utilities import print_warning




class CythonFallbackImporter:
    def __init__(self, auto_compile=False):
        self.auto_compile = auto_compile  # store the auto_compile option
        # print('----------------auto_compile', self.auto_compile)
        try:
            from Cython.Build import cythonize
            self.cythonize = cythonize
        except ImportError:
            self.cythonize = None

        print('has cython:', self.cythonize)


    def find_spec(self, fullname, path=None, target=None):
        # if not fullname.endswith('.py'):
        #     print('skip', fullname)
        #     return None  # only handle .py files
        

        # print(f"Trying to load module: {fullname}")
        if path is None:
            path = sys.path  # use default sys.path if no path provided

        path = [Path(p) for p in path]
        
        local_paths = [p for p in path if 'site-packages' not in p.parts and 'lib' not in p.parts]
        # print('aaaaaaaaaa', path)
        # return
        compiled_filename = f"{fullname.replace('.', '/')}.cpython-{sys.version_info[0]}{sys.version_info[1]}.so"  # compiled file name
        pure_python_filename = f"{fullname.replace('.', '/')}.py"  # pure python file name
        pyx_filename = f"{fullname.replace('.', '/')}.apyx"  # .pyx file name for Cython

        # check for the compiled file first
        for directory in local_paths:
            compiled_path = directory / compiled_filename  # use Path directly
            if compiled_path.exists():
                print('import compiled:', fullname)
                return importlib.util.spec_from_file_location(fullname, str(compiled_path))

        # if not found and auto_compile is enabled, try to compile the .pyx file
        if self.auto_compile and self.cythonize is not None:
            for directory in local_paths:
                python_path = directory / pure_python_filename
                pyx_path = directory / pyx_filename  # construct path to .pyx file
                # if any(ignored in python_path.parts for ignored in ['Cython', 'site-packages']):
                #     print('ignore:', python_path)
                #     break
                
                print('try to auto compile:', python_path)
                # if pyx_path.exists():
                with pyx_path.open('w') as destination:
                    with open(directory / pure_python_filename, 'r') as source:
                        destination.write(source.read())
                    print(';;;;;;;;;;;;;create', pyx_path, 'from', directory / pure_python_filename)
                    try:
                        print(f"Compiling {pyx_path} with Cython...")
                        self.cythonize(pyx_path, force=True)
                        compiled_filename = f"{module_name}.cpython-{sys.version_info[0]}{sys.version_info[1]}.so"
                        print(f"successfully compiled {compiled_filename}")
                        compiled_path = Path(directory) / compiled_filename
                        return importlib.util.spec_from_file_location(fullname[:-4], str(compiled_path))

                    except Exception as e:
                        print_warning(f"Failed to compile {pyx_path} with Cython: {e}")
                        break

        # fallback to pure Python file if no compiled file is found
        for directory in path:
            python_path = directory / pure_python_filename  # use Path directly
            if python_path.exists():
                print_warning(f'import cython module failed, falling back to python for: {Path(python_path).name}')
                return importlib.util.spec_from_file_location(fullname, str(python_path))

        print('failed import')
        return None


def replace_import_statement(auto_compile=False):
    cython_importer = CythonFallbackImporter(auto_compile=auto_compile)
    # print('---------', cython_importer.pyximport)
    if auto_compile and cython_importer.cythonize is None:
        print_warning('''trying to use auto_compile, but pyximport wasn't found (already compiled modules can still be imported)''')

    sys.meta_path.insert(0, cython_importer)  # register custom importer


if __name__ == '__main__':
    replace_import_statement(auto_compile=True)  # change this to True to enable auto-compilation
    import grid_layout
    print('----', grid_layout)
    # from ursina.scripts.grid_layout import grid_layout  # test the import
