from ursina import *


# WORLD_NORMAL

# void vert():
#     gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
#     texcoord = p3d_MultiTexCoord0;

#     world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
#     vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
#     vertex_color = p3d_Color;


def triplanar_mapping_frag():
    blend:Vec3 = TriPlanarBlendWeightsConstantOverlap(WORLD_NORMAL)

    albedoX:Vec3 = texture(side_texture, vertex_world_position.zy * side_texture_scale).rgb*blend.x
    albedoY:Vec3 = texture(side_texture, vertex_world_position.xz * side_texture_scale).rgb*blend.y
    albedoZ:Vec3 = texture(side_texture, vertex_world_position.xy * side_texture_scale).rgb*blend.z
    a = 1.0
    b:float = 2.0
    b = 2.5

    if WORLD_NORMAL.y > .0:
        albedoY = texture(TEXTURE, vertex_world_position.xz * texture_scale.xy).rgb*blend.y

    triPlanar:Vec3 = (albedoX + albedoY + albedoZ)

    return Vec4(triPlanar.rgb, 1) * VERTEX_COLOR




def get_indent(str):
    if (not str or not str.strip()):
        return 0

    return (len(str) - len(str.lstrip())) / 4


def indent_to_curly(text):
    # // add brackets based on indentation
    current_indent = 0
    after_statement_indents = []
    lines = [l for l in text.split('\n') if l]
    lines.append('')

    for i in range(1, len(lines)):
        if (lines[i-1].endswith('=') or lines[i-1].endswith('+') or lines[i-1].endswith('(')):
            continue

        prev_line_indent = get_indent(lines[i-1])
        current_line_indent = get_indent(lines[i])

        if (current_line_indent > prev_line_indent):
            lines[i-1] += ' {'
            current_indent = current_line_indent

        if (current_line_indent < prev_line_indent):
            for j in range(int(current_indent - current_line_indent)):
                lines[i-1] += '\n' + ('    '*int(current_indent-j-1)) + '}'

            current_indent = current_line_indent

    return '\n'.join(lines)


def convert_if_statements(text):
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if lines[i].endswith(':'):
            lines[i] = lines[i][:-1]

        # ifs
        if lines[i].lstrip().startswith('if '):
            lines[i] = lines[i].replace('if ', 'if (')
            lines[i] = lines[i] + ')'

        # elifs
        elif l.lstrip().startswith('elif '):
            lines[i] = lines[i].replace('elif ', 'else if (')
            lines[i] = lines[i] + ')'


    return '\n'.join(lines)


def add_semicolons(text):
    lines = text.split('\n')

    special_characters = '{}'
    for i in range(len(lines)):
        continue_outer = False
        if not lines[i]:
            continue

        for char in special_characters:
            if lines[i].endswith(char):
                continue_outer = True

        if continue_outer:
            continue

        lines[i] = f'{lines[i]};'

    return '\n'.join(lines)


def get_return_type(text):
    returns = [l for l in text.split('\n') if l.lstrip().startswith('return ')]
    if not returns:
        raise Exception("function doesn't return anything")

    var = returns[0].split('return ')[1]
    if ' ' in var:
        var = var.split(' ')[0]
    if '(' in var:
        var = var.split('(')[0]

    return var


def convert_function_declaration(text):
    lines = text.split('\n')
    header = lines[0]
    name = header.lstrip('def ').split('(')[0]

    return_type = get_return_type(text)

    lines[0] = f'{return_type} {name}()'

    return '\n'.join(lines)


def _contains_special_character(text):
    specials = '?/()[]{}<>;'
    for char in specials:
        if char in text:
            return True
    return False


# def get_variables(text):
    # variables = dict()
    # import re
    # delimiters = (' ','\n','+','-','*','/',',','=')
    # regex_pattern = '|'.join(map(re.escape, delimiters))
    # keywords = ('return', 'if', 'elif', 'def', 'for')
    # # return [word.split('.')[0] for word in re.split(regex_pattern, text) if word and not _contains_special_character(word) and not _is_keyword(word)]
    # for word in re.split(regex_pattern, text):
    #     print('-----------', word)
    #     if not word or _contains_special_character(word) or word in keywords or word.isnumeric():
    #         # print('skip:', word)
    #         continue
    #
    #     # print('w', word)
    #     data_type = None
    #     if ':' in word:
    #         word, data_type = word.split(':', 1)
    #
    #     variables[word.split('.')[0]] = data_type
    #
    # return variables

import ast

def get_variables_types_and_values_in_function(source_code):
    tree = ast.parse(source_code)

    # Find the target function
    target_function = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            target_function = node
            # break

            # if not target_function:
            #     raise ValueError(f"Function '{function_name}' not found in the code.")

            # Extract variable names, their associated type hints, and values within the function
            variables_info = {}
            for sub_node in ast.walk(target_function):
                if isinstance(sub_node, ast.Assign):
                    for target in sub_node.targets:
                        if isinstance(target, ast.Name):
                            variable_name = target.id
                            type_hint = None
                            value = None

                            if sub_node.value:
                                value = ast.get_source_segment(source_code, sub_node.value).strip()

                            if isinstance(sub_node.value, ast.AnnAssign):
                                # If there's a type hint in the AnnAssign, use it
                                type_hint = ast.get_source_segment(source_code, sub_node.value.annotation).strip()

                            variables_info[variable_name] = {'type_hint': type_hint, 'value': value, 'function': node.name}
                            print('add:', variable_name, variables_info[variable_name])

            return variables_info



import inspect
def convert_to_glsl(func):
    result = ''
    # source_code = inspect.getsource(func)
    # # variables = get_variables(source_code)
    # variables = get_variables_types_and_values_in_function(source_code)
    #
    # source_code = convert_function_declaration(source_code)
    # source_code = convert_if_statements(source_code)
    # source_code = indent_to_curly(source_code)
    # source_code = add_semicolons(source_code)
    #

    # print(source_code)
    # for key, value in variables.items():
    #     # type, value, func = value
    #     print(key, value)

    tree = ast.parse(inspect.getsource(func))
    print(ast.dump(tree, indent=4))
    for e in tree.body:
        # print(e)
        func_def = e
        print('functiopn name:', func_def.name)
        # func_def.args
        # func_def.body
        variables = set()

        for action in func_def.body:
            if isinstance(action, (ast.AnnAssign)):
                var_name = action.target.id
                data_type = action.annotation.id
                print(f'{data_type} {var_name} = {action.value};')
                variables.add(var_name)

            if isinstance(action, (ast.Assign)):
                var_name = action.targets[0].id
                data_type = '???'
                # datatype = guess_type(action.value)
                variables.add(var_name)
                print(f'{data_type} {var_name} = {action.value};')
                # print('new var:', 'name:', action.targets[0].id, 'type:', '???', 'value:', action.value)


    # function_info = inspect.getmembers(func)
    # local_variables = [var for var in function_info if inspect.isframe(var[1])]
    # variable_names = local_variables[0][1].f_locals.keys()
    # print(function_info)
    # return lines
if __name__ == '__main__':
    convert_to_glsl(triplanar_mapping_frag)


# from unlit_shader import vert as unlit_shader_vert
# my_shader = wind_shader + unlit_shader + fog_gradient_shader + lit_with_shadows_shader + triplanar_shader
#
# if __name__ == '__main__':
#     import ast
