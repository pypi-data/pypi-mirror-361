import pyximport
import os
import sys
import inspect
import importlib.util
import subprocess
import sysconfig
from pathlib import Path

# Install pyximport hooks for automatic compilation
pyximport.install()


def get_function_code(func):
    code_obj = func.__code__        # Extract the code object from the function
    # Get the function's source code (this assumes you have access to the source code)
    try:
        # Retrieve the actual source code of the function (if available)
        import inspect
        source_code = inspect.getsource(func)
        if source_code[0] == '@':
            source_code = 'def ' + source_code.split('\ndef ', 1)[1]    # remove decorators
            print('--...................\n', source_code)
    except Exception as e:
        print(f'Error retrieving function source: {e}')
        return None

    return source_code


def list_variables_and_types(source_code, annotations):
    import re
    # Use regex to find assignments in the source code
    pattern = r"(\w+)\s*[:=]\s*(.*)"
    variables = re.findall(pattern, source_code)
    
    variable_types = {}

    # Loop over the variables to try to infer types from the annotations
    # print('-------', func.__annotations__)
    for varname, expr in variables:
        if varname in variable_types:
            continue

        var_annotation = annotations.get(varname, None)
        if var_annotation is not None:
            variable_types[varname] = var_annotation
        try:
            # Evaluate the expression to guess the type
            # print('fffffffffffffff', expr)
            # if not expr.startswith('(') and not expr.startswith('[') and '(' in expr:
            #     variable_types[varname] = expr.split('(',1)[0]
            #     continue
            if expr.startswith('Vec3('):
                variable_types[varname] = Vec3
                continue
                

            evaluated_value = eval(expr)
            # print('aa', varname, evaluated_value)
            variable_types[varname] = type(evaluated_value)
        except Exception as e:
            # If evaluation fails, mark type as Unknown
            # print('e:', e)
            variable_types[varname] = None

    return source_code, variable_types


def guess_types(source_code, annotations):
    source_code, variables = list_variables_and_types(source_code, annotations)
    # print('aaaaaaaaaaaaaaaaaaaaaadding types to ', source_code, variables)
    for name, vartype in variables.items():
        if not vartype:
            continue
        # print(':::::::::::::::::::::', name, ':', vartype.__name__)
        if vartype == Vec3:
            # print('REPLACPEL VEC###################################', name, f' = {vartype.__name__}(' in source_code)
            source_code = source_code.replace(f' = {vartype.__name__}(', f' = (')
            source_code = source_code.replace(f'{name} = ', f'{name}:{'tuple[cython.double, cython.double, cython.double]'} = ')
            # print('REPLACPEL VEC###################################', source_code)
        # fubcc
    source_code = source_code.replace(':Vec3,', ':tuple[cython.double, cython.double, cython.double],')
    source_code = source_code.replace(':Vec3)', ':tuple[cython.double, cython.double, cython.double])')
    source_code = source_code.replace(' -> Vec3:', ' -> tuple[cython.double, cython.double, cython.double]:')

    return source_code


def compile_pyx_file(pyx_file):
    # Get the name of the compiled shared object
    c_file_path = pyx_file.with_suffix('').with_suffix('.c')
    compiled_extention_module = pyx_file.with_suffix('').with_suffix('.so')
    python_interpreter = sys.executable
    include_path = sysconfig.get_paths()['include']

    subprocess.run([
        python_interpreter, 
        '-m', 
        'cython', 
        '-a', # annotated 
        str(pyx_file), 
        '-o', 
        str(c_file_path)
    ], check=True)

    subprocess.run([
        'gcc',
        '-shared',
        '-fPIC', 
        '-O3',
        f'-I{include_path}',
        str(c_file_path), 
        "-o", 
        str(compiled_extention_module)
    ], check=True)
    
    return compiled_extention_module



def pyximport(pyx_file, module_name):
    compiled_extention_module = compile_pyx_file(pyx_file)
    
    # Add the path to the compiled file to sys.path
    module_dir = compiled_extention_module.parent
    if module_dir not in sys.path:
        sys.path.append(module_dir)
    
    # Dynamically import the compiled module
    spec = importlib.util.spec_from_file_location(module_name, compiled_extention_module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def load_module_from_path(module_file_path, name=''):
    if not name:
        name = module_file_path.stem

    if not module_file_path.exists():
        raise FileNotFoundError(f'The module file {module_file_path} does not exist.')

    if module_file_path.suffix == '.pyx':
        pyximport(module_file_path, name)

    elif module_file_path.suffix == '.py':
        sys.path.append(str(module_file_path.parent))
    
    else:
        raise ValueError('Only .py and .pyx files are supported.')

    module = importlib.import_module(name)
    return module


__autocythonize__ = True

from functools import wraps

def cythonize_function(func=None, include=None):
    '''
    A decorator to compile a Python function into a Cython function at runtime.
    '''
    if include is None:
        include = [] 
    else:
        original_include_count = len(include)
        include = tuple(set(include))
        if len(include) < original_include_count:
            print_warning('Included more than one copy in:', func)


    if func is None:
        return lambda func: cythonize_function(func, include=include)
    # def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not __autocythonize__:
            return func(*args, **kwargs)

        # Get the current script's filename without extension
        script_name = Path(__file__).stem
        func_name = func.__name__
        current_file = Path(__file__)

        # Construct a unique filename based on the script name and the function name
        pyx_file_path = current_file.parent / '__cythonized__' / f'{current_file.stem}_{func_name}.pyx'
        # print('---------', pyx_file_path)
        import textwrap
        module_code = textwrap.dedent('''\
            # generated by cythonize_function decorator
            cimport cython

            ''')

        print("Functions to include:", include)
        for incl in include:
            include_code = get_function_code(incl)
            annotations = incl.__annotations__
            include_code = guess_types(include_code, annotations)
            # print('------------------iiiiiiiiiiiiiiiiii', 'including function:', incl.__name__, include_code)
            module_code += textwrap.dedent('''\
                @cython.boundscheck(False)  # Disable bounds checking for performance
                @cython.wraparound(False)   # Disable negative indexing
                @cython.cfunc               # C function, not called from Python
            ''') + include_code + '\n\n'
            # module_code += include_code

        func_code = get_function_code(func)
        annotations = func.__annotations__
        func_code = guess_types(func_code, annotations)

        module_code += textwrap.dedent('''\
            @cython.boundscheck(False)  # Disable bounds checking for performance
            @cython.wraparound(False)   # Disable negative indexing
        ''') + func_code

        pyx_file_path.parent.mkdir(exist_ok=True)

        with open(pyx_file_path, 'w') as pyx_file:
            pyx_file.write(module_code)

        # Ensure the current directory is in the sys.path
        sys.path.insert(0, pyx_file_path.parent)
        # print('paths:', sys.path)

        import importlib
        # print('importing:', str(pyx_file_path), 'as', pyx_file_path.stem)

        compiled_module = load_module_from_path(pyx_file_path, pyx_file_path.stem)
        # print('compiled module:', compiled_module)

        # Replace the original function with the compiled one
        cython_func = getattr(compiled_module, func_name)
        sys.path.pop(0)
        return cython_func(*args, **kwargs)
        # os.unlink(pyx_file_path)    # Clean up the temporary file

    return wrapper
    # return decorator

# __autocythonize__ = False
# Example usage
import cython

from ursina import Vec3

def _subtract(v1:Vec3, v2:Vec3) -> Vec3:
    result = Vec3(v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])
    return result

@cythonize_function(include=[_subtract, ])
def example_function():
    # from cythonizer__subtract import _subtract
    compiled = 'compiled' if __file__.endswith('.so') else 'pure python'
    from time import perf_counter
    import random
    t = perf_counter()
    
    result = Vec3(0.0, 0.0, 0.0)

    # result: tuple_with_three_floats = (0.0, 0.0, 0.0)
    other = Vec3(1.0, 2.0, 3.0)
    for i in range(1_000_000):
        other = Vec3(1.0, 2.0, 3.0)
        result = _subtract(result, other)

    print('-----:', compiled, perf_counter() - t)
    return result

# Test the function
if __name__ == '__main__':
    ...
    print(_subtract(Vec3(2,2,2), Vec3(1,1,1)))
    result = example_function()
    print('Result:', result)
