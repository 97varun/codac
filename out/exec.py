from pycparser import parse_file, c_generator, c_parser
from pycparser.c_ast import *
from operator import attrgetter
from copy import deepcopy
from pycparser.plyparser import Coord
import os
import re


def expression(sem):
    '''converts semantic for expression to pycparser ast node'''
    if sem[0] == 'name':
        return ID(sem[1])
    elif sem[0] == 'value':
        return Constant('int', str(sem[1]))
    elif sem[0] == 'str':
        return Constant('string', f'"{sem[1]}"')
    elif sem[0] == '()':
        return FuncCall(
            ID(sem[1]),
            None if sem[2] is None
            else ExprList(list(map(expression, sem[2])))
        )
    elif sem[0] == '[]':
        return ArrayRef(expression(sem[1]), expression(sem[2]))
    elif len(sem) == 2:
        return UnaryOp(sem[0], expression(sem[1]))
    elif len(sem) == 3:
        return BinaryOp(sem[0], expression(sem[1]), expression(sem[2]))


def array_decl(name, type, size):
    '''converts semantic for array declaration to pycparser ast node'''
    if len(size) == 1:
        return ArrayDecl(
            TypeDecl(name, [], IdentifierType([type])),
            Constant('int', str(size[0])), []
        )
    return ArrayDecl(array_decl(name, type, size[1:]),
                     Constant('int', str(size[0])), [])


def loop_decl(type):
    '''converts semantic for loops to pycparser ast node'''
    if type == 'for':
        return For(None, None, None, Compound([]))
    elif type == 'while':
        return While(Constant('boolean', 'true'), Compound([]))


def var_decl(name, type, value=None, modifier=None):
    '''converts semantic for variable declaration to pycparser ast node'''
    typ_decl = TypeDecl(name, [], IdentifierType([type]))
    if modifier is not None:
        typ_decl = PtrDecl([], typ_decl)
    return Decl(
        name, [], [], [],
        typ_decl,
        value if value is None else expression(value),
        None
    )

spec = {
    # variable and pointer
    'declare_variable_req': {'name': None, 'type': None, 'value': 'opt',
                             'modifier': 'opt'},
    'declare_variable_tpl': var_decl,

    # array
    'declare_array_req': {'name': None, 'type': None, 'size': None},
    'declare_array_tpl': lambda name, type, size: Decl(
        name, [], [], [],
        array_decl(name, type, size),
        None, None
    ),

    # assignment
    'declare_assignment_req': {'lhs': None, 'rhs': None},
    'declare_assignment_tpl': lambda lhs, rhs: Assignment(
        '=',
        expression(lhs),
        expression(rhs)
    ),

    # include
    'include_package_req': {'name': None, 'type': 'lib'},
    'include_package_tpl': lambda name, type:
    '#include"{0}.h"'.format(name) if type == 'own'
    else '#include<{0}.h>'.format(name),

    # if
    'declare_if_req': {},
    'declare_if_tpl': lambda: If(Constant('boolean', 'true'),
                                 Compound([]), None),

    'declare_if_else_req': {},
    'declare_if_else_tpl': lambda: If(Constant('boolean', 'true'),
                                      Compound([]), Compound([])),

    'add_condition_req': {'cond': None},
    'add_condition_tpl': expression,

    'add_else_req': {},
    'add_else_tpl': lambda: Compound([]),

    'add_else_if_req': {},
    'add_else_if_tpl': lambda: If(Constant('boolean', 'true'),
                                  Compound([]), None),

    # loops
    'declare_loop_req': {'type': None},
    'declare_loop_tpl': loop_decl,

    'add_init_req': {'name': None, 'type': None, 'value': 'opt'},
    'add_init_tpl': var_decl,

    'add_update_req': {'updates': None},
    'add_update_tpl': lambda updates: expression(updates),

    # function
    'declare_function_req': {'name': None, 'type': 'void'},
    'declare_function_tpl': lambda name, type: FuncDef(
        Decl(name, [], [], [], FuncDecl(
                                    ParamList([]),
                                    TypeDecl(name, [], IdentifierType([type]))
                                ), None, None),
        [],
        Compound([]),
    ),

    'declare_func_call_req': {'name': None, 'parameters': 'opt'},
    'declare_func_call_tpl': lambda name, parameters: FuncCall(
        ID(name),
        None if parameters is None
        else ExprList(list(map(expression, parameters)))
    ),

    'declare_return_req': {'value': None},
    'declare_return_tpl': lambda value: Return(expression(value)),

    'add_parameter_req': {'name': None, 'type': None,
                          'modifier': 'opt', 'position': 'opt'},
    'add_parameter_tpl': lambda name, type, modifier, position:
        (var_decl(name, type, None, modifier), position),
}


def get_ag(ast, attrs):
    ag = None
    for attr in attrs:
        if hasattr(ast, attr):
            return attrgetter(attr)
    return ag


def coord_first_line(ast):
    return ast.coord.line


def coord_last_line(ast):
    if isinstance(ast, Compound):
        if ast.block_items is None or len(ast.block_items) == 0:
            return ast.coord.line + 1
        return coord_last_line(ast.block_items[-1]) + 1
    elif isinstance(ast, If):
        return coord_last_line(ast.iftrue if ast.iffalse is None
                               else ast.iffalse)
    elif isinstance(ast, For) or isinstance(ast, While):
        return coord_last_line(ast.stmt)
    elif isinstance(ast, FuncDef):
        return coord_last_line(ast.body)
    return ast.coord.line


def add_condition(stmt, pos, cond):
    '''add condition to if, for and while'''
    if hasattr(stmt, 'cond'):
        stmt.cond = cond
        return None, True
    return None, False


def add_parameter(stmt, pos, param):
    '''add parameter to function declaration'''
    if not hasattr(stmt, 'decl'):
        return None, False
    if stmt.decl.type.args is None:
        stmt.decl.type.args = ParamList([param[0]])
    else:
        idx = param[1]
        if idx is None:
            idx = len(stmt.decl.type.args.params) + 1
        idx -= 1
        stmt.decl.type.args.params.insert(idx, param[0])
    return None, True


def add_init(stmt, pos, init):
    '''add initialization to for'''
    if not hasattr(stmt, 'init'):
        return None, False
    if stmt.init is None:
        stmt.init = DeclList([init])
    else:
        stmt.init.decls.append(init)
    return None, True


def add_update(stmt, pos, upd):
    '''add update statement to for'''
    if not hasattr(stmt, 'next'):
        return None, False
    if stmt.next is None:
        stmt.next = ExprList([upd])
    elif isinstance(stmt.next, UnaryOp) or isinstance(stmt.next, BinaryOp):
        stmt.next = ExprList([stmt.next, upd])
    else:
        stmt.next.exprs.append(upd)
    return None, True


def add_else(stmt, pos, els):
    '''adds else block to if statement'''
    if not hasattr(stmt, 'iffalse'):
        return None, False
    if stmt.iffalse is None:
        coord = Coord('file', coord_last_line(stmt) + 2, 0)
        stmt.iffalse = els
        return coord, True
    elif isinstance(stmt.iffalse, If):
        return add_else(stmt.iffalse, pos, els)
    return None, True


def add_else_if(stmt, pos, elseif):
    if not hasattr(stmt, 'iffalse'):
        return None, False
    old_iffalse = stmt.iffalse
    coord = Coord('file', coord_last_line(stmt) + 2, 0)
    stmt.iffalse = elseif
    stmt.iffalse.iffalse = old_iffalse
    return coord, True


def add_statement(stmt, pos, attr):
    '''add statement to ast'''
    ag = get_ag(stmt, ['body', 'iftrue', 'stmt'])
    coord = ag(stmt).coord
    stmt = ag(stmt).block_items
    stmt.insert(pos, attr)
    if len(stmt) > 0 and pos > 0:
        coord.line = stmt[pos - 1].coord.line
    coord.line += 1
    return coord, True


def declare_variable(stmt, pos, decl):
    '''add variable declaration to ast'''
    return add_statement(stmt, pos, decl)


def declare_array(stmt, pos, decl):
    '''add variable declaration to ast'''
    return add_statement(stmt, pos, decl)


def declare_assignment(stmt, pos, assgn):
    '''add assignment statement to ast'''
    return add_statement(stmt, pos, assgn)


def declare_if(stmt, pos, if_stmt):
    '''add if statement to ast'''
    coord, found = add_statement(stmt, pos, if_stmt)
    coord.line += 1
    return coord, found


def declare_if_else(stmt, pos, if_else):
    '''adds if else statement to ast'''
    coord, found = add_statement(stmt, pos, if_else)
    coord.line += 1
    return coord, found


def declare_loop(stmt, pos, loop):
    '''add loop statement to ast'''
    coord, found = add_statement(stmt, pos, loop)
    coord.line += 1
    return coord, found


def declare_func_call(stmt, pos, func_call):
    '''add function call to ast'''
    return add_statement(stmt, pos, func_call)


def declare_return(stmt, pos, ret):
    '''add return statement to ast'''
    return add_statement(stmt, pos, ret)


def find_pos(stmt, line):
    ag = get_ag(stmt, ['body', 'iftrue', 'stmt'])
    if ag(stmt).block_items is None:
        ag(stmt).block_items = []
    stmt = ag(stmt).block_items
    for i in range(len(stmt)):
        first_line = coord_first_line(stmt[i])
        last_line = coord_last_line(stmt[i])
        if line < first_line:
            return i
        elif line == last_line:
            return i + 1
    return -1


def check_node(stmt, line, attr):
    '''checks if the current node is the place to insert,
       calls the appropriate insert function'''
    first_line = coord_first_line(stmt)
    last_line = coord_last_line(stmt)
    if line >= first_line and line < last_line:
        pos = find_pos(stmt, line)
        return globals()[attr['method']](stmt, pos, attr['arg'])
    return None, False


def find_node(stmt, line, attr):
    '''traverses the ast to find the correct node to insert'''
    if stmt is None:
        return None, False
    for i in range(len(stmt)):
        children = []
        # If
        if isinstance(stmt[i], If):
            if stmt[i].iftrue.block_items is not None:
                children = list(stmt[i].iftrue.block_items)
            if stmt[i].iffalse is not None:
                if isinstance(stmt[i].iffalse, If):
                    children.append(stmt[i].iffalse)
                elif stmt[i].iffalse.block_items is not None:
                    children.append(*stmt[i].iffalse.block_items)
        # For and While
        elif isinstance(stmt[i], For) or isinstance(stmt[i], While):
            children = stmt[i].stmt.block_items
        # FuncDef
        elif isinstance(stmt[i], FuncDef):
            children = stmt[i].body.block_items
        coord, found = find_node(children, line, attr)
        if found:
            return coord, found
        coord, found = check_node(stmt[i], line, attr)
        if found:
            return coord, found
    return None, False


def find_range(stmt, name):
    '''traverses the ast to find the correct lines to delete'''
    if stmt is None:
        return None, False
    for i in range(len(stmt)):
        children = []
        # If
        if isinstance(stmt[i], If):
            if stmt[i].iftrue.block_items is not None:
                children = list(stmt[i].iftrue.block_items)
            if stmt[i].iffalse is not None:
                if isinstance(stmt[i].iffalse, If):
                    children.append(stmt[i].iffalse)
                elif stmt[i].iffalse.block_items is not None:
                    children.append(*stmt[i].iffalse.block_items)
        # For and While
        elif isinstance(stmt[i], For) or isinstance(stmt[i], While):
            children = stmt[i].stmt.block_items
        # FuncDef
        elif isinstance(stmt[i], FuncDef):
            children = stmt[i].body.block_items
        rng, found = find_range(children, name)
        if found:
            return rng, found

        if hasattr(stmt[i], 'decl') and stmt[i].decl.name == name or\
           isinstance(stmt[i], Decl) and stmt[i].name == name:
                return (coord_first_line(stmt[i]),
                        coord_last_line(stmt[i])), True
    return None, False


def req_checker(name, sem):
    req = spec[name + '_req']
    tpl = spec[name + '_tpl']
    args = []
    for elem in req.keys():
        if elem not in sem:
            # error: missing field
            if req[elem] is None:
                msg = '{0} missing'.format(elem)
                err = {'output': 'Error: ' + msg + '\n' + str(sem),
                       'error': 'Could not generate output.\
                           \nMissing Field: ' + elem}
                return err
            elif req[elem] is 'opt':
                args.append(None)
            else:
                args.append(req[elem])
        else:
            args.append(sem[elem])
    return tpl(*args)


def handle_req(ext, fmt, sem, line):
    line -= len(fmt['includes'])
    req_type = '{0}_{1}'.format(sem['request'], sem['construct'])
    node = req_checker(req_type, sem)
    coord = Coord('file', line, 0)

    # error: missing field
    if isinstance(node, dict):
        return coord, node

    if req_type == 'declare_function':
        coord.line = 3
        ext.insert(0, node)
    elif req_type == 'include_package':
        fmt['includes'].append(node)
    else:
        coord, found = find_node(ext, line, {'method': req_type, 'arg': node})
        # error: could not find node to insert at
        if found is False:
            err = {'output': 'ASTInsertErr' + '\n' + str(sem),
                   'Error': 'Could not insert into the A. S. T.'}
            return coord, err
    if coord is None:
        coord = Coord('file', line, 0)
    if isinstance(node, tuple):
        node = node[0]
    coord.line += len(fmt['includes'])
    return coord, node


def preprocess(filename):
    '''extracts formatting and includes from file'''
    fmt = {'includes': []}
    src = ''
    with open(filename) as file:
        for line in file:
            if line.startswith('#'):
                fmt['includes'].append(line)
            else:
                src += line
        src.lstrip('\n')
    return src, fmt


def postprocess(fmt, replace):
    '''adds formatting and includes to replace'''
    replace = re.sub('\n+', '\n', replace)
    replace = re.sub('else\s+if', 'else if', replace)
    replace = ''.join(fmt['includes']) + '\n' + replace
    return replace


def generate_code(sems, filename, line):
    generator = c_generator.CGenerator()
    parser = c_parser.CParser()

    src, fmt = preprocess(filename)
    ast = parser.parse(src)

    codes = []
    for sem in sems:
        # error : if the first result has error, then exit
        if len(codes) == 1 and isinstance(codes[0], dict):
            if 'error' in codes[0]:
                break
        if 'request' not in sem or 'construct' not in sem or\
           sem['request'] not in ['declare', 'add', 'include', 'edit']:
            if 'request' in sem and sem['request'] in ['navigate']:
                codes.append(sem)
            else:
                codes.append({'output': 'UnknownReqError' + '\n' + str(sem),
                              'error': 'Could not understand request.\
                                  \nSem : ' + str(sem)})
            continue

        # editing
        if sem['request'] == 'edit':
            if 'name' in sem:
                rng, found = find_range(ast.ext, sem['name'])
            if rng is None:
                error = {'error': 'could not find name'}
                codes.append(error)
            else:
                if rng[0] == rng[1]:
                    rng = (rng[0], )
                sem['value'] = rng
                codes.append(sem)
            continue

        new_ext = deepcopy(ast.ext)
        new_fmt = deepcopy(fmt)
        coord, node = handle_req(new_ext, new_fmt, sem, line)
        if isinstance(node, dict):
            codes.append(node)
            continue
        op = node
        # op is string for include_package
        if not isinstance(op, str):
            op = generator.visit(node)
        # if the request threw error
        rp = generator.visit(FileAST(new_ext))
        rp = postprocess(new_fmt, rp)
        codes.append({'output': op, 'replace': rp,
                     'cursor': coord.line})

    return codes


def get_scope_variables():
    return ['a', 'b', 'c', 'd', 'x', 'y', 'z', 'i', 'j', 'k', 'g', 'h',
            'found', 'element', 'program_count', 'test_case', 'ptr',
            'abc', 'max', 'sum', 'min', 'date', 'result', 'limit', 'main']

if __name__ == '__main__':
    codes = generate_code(
        [{'request': 'add', 'construct': 'parameter',
          'name': 'x', 'type': 'int'}],
        'hello.c',
        4
    )
    print(codes)
