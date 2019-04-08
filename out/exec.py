from pycparser import parse_file, c_generator
from pycparser.c_ast import *
from operator import attrgetter
from copy import deepcopy
from pycparser.plyparser import Coord
import os


def expression(sem):
    if sem[0] == 'name':
        return ID(sem[1])
    elif sem[0] == 'value':
        return Constant('int', str(sem[1]))
    elif len(sem) == 2:
        return UnaryOp(sem[0], expression(sem[1]))
    elif len(sem) == 3:
        return BinaryOp(sem[0], expression(sem[1]), expression(sem[2]))


def add_condition_tpl(sem):
    if sem[0] == 'name':
        return ID(sem[1])
    elif sem[0] == 'value':
        return Constant('int', str(sem[1]))
    return BinaryOp(
        sem[0],
        add_condition_tpl(sem[1]),
        add_condition_tpl(sem[2])
    )


def array_decl(name, type, size):
    if len(size) == 1:
        return ArrayDecl(
            TypeDecl(name, [], IdentifierType([type])),
            Constant('int', str(size[0])), []
        )
    return ArrayDecl(array_decl(name, type, size[1:]),
                     Constant('int', str(size[0])), [])


def loop_decl(type):
    if type == 'for':
        return For(None, None, None, Compound([]))
    elif type == 'while':
        return While(None, Compound([]))


def var_decl(name, type):
    return Decl(
        name, [], [], [],
        TypeDecl(name, [], IdentifierType([type])), None, None
    )


def ptr_decl(name, type):
    pass

spec = {
    # variable
    'declare_variable_req': ['name', 'type'],
    'declare_variable_tpl': var_decl,

    # array
    'declare_array_req': ['name', 'type', 'size'],
    'declare_array_tpl': lambda name, type, size: Decl(
        name, [], [], [],
        array_decl(name, type, size),
        None, None
    ),

    # assignment
    'declare_assignment_req': ['lhs', 'rhs'],
    'declare_assignment_tpl': lambda lhs, rhs: Assignment(
        '=',
        ID(lhs[1]),
        expression(rhs)
    ),

    # include
    'include_package_req': ['name', 'type'],
    'include_package_tpl': lambda name, type:
    '#include"{0}"'.format(name) if type == 'own'
    else '#include<{0}>'.format(name),

    # if
    'declare_if_req': [],
    'declare_if_tpl': lambda: If(Constant('boolean', 'true'),
                                 Compound([]), None),

    'declare_if-else_req': [],
    'declare_if-else_tpl': lambda: If(Constant('boolean', 'true'),
                                      Compound([]), Compound([])),

    'add_condition_req': ['cond'],
    'add_condition_tpl': add_condition_tpl,

    'add_else_req': [],
    'add_else_tpl': lambda: Compound([]),

    'add_else_if_req': [],
    'add_else_if_tpl': lambda: If(Constant('boolean', 'true'),
                                  Compound([]), None),

    # loops
    'declare_loop_req': ['type'],
    'declare_loop_tpl': loop_decl,

    'add_init_req': ['name', 'type'],
    'add_init_tpl': var_decl,

    'add_update_req': ['updates'],
    'add_update_tpl': lambda updates: expression(updates),

    # function
    'declare_function_req': ['name', 'type'],
    'declare_function_tpl': lambda name, type: FuncDef(
        Decl(name, [], [], [], FuncDecl(
                                    ParamList([]),
                                    TypeDecl(name, [], IdentifierType([type]))
                                ), None, None),
        [],
        Compound([]),
    ),

    'declare_func_call_req': ['name', 'parameters'],
    'declare_func_call_tpl': lambda name, parameters: FuncCall(
        ID(name),
        ExprList(list(map(expression, parameters)))
    ),

    'declare_return_req': ['value'],
    'declare_return_tpl': lambda value: Return(expression(value)),
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
        return True
    return False


def add_parameter(stmt, pos, param):
    '''add parameter to function declaration'''
    if not hasattr(stmt, 'decl'):
        return False
    if stmt.decl.type.args is None:
        stmt.decl.type.args = ParamList([param])
    else:
        stmt.decl.type.args.params.append(param)
    return True


def add_init(stmt, pos, init):
    '''add initialization to for'''
    if not hasattr(stmt, 'init'):
        return False
    if stmt.init is None:
        stmt.init = DeclList([init])
    else:
        stmt.init.decls.append(init)
    return True


def add_update(stmt, pos, upd):
    '''add update statement to for'''
    if not hasattr(stmt, 'next'):
        return False
    if stmt.next is None:
        stmt.next = ExprList([upd])
    elif isinstance(stmt.next, UnaryOp) or isinstance(stmt.next, BinaryOp):
        stmt.next = ExprList([stmt.next, upd])
    else:
        stmt.next.exprs.append(upd)
    return True


def add_else(stmt, pos, els):
    '''adds else block to if statement'''
    if not hasattr(stmt, 'iffalse'):
        return False
    if stmt.iffalse is None:
        stmt.iffalse = els
        return True
    elif isinstance(stmt.iffalse, If):
        return add_else(stmt.iffalse, pos, els)
    return True


def add_else_if(stmt, pos, elseif):
    if not hasattr(stmt, 'iffalse'):
        return False
    old_iffalse = stmt.iffalse
    stmt.iffalse = elseif
    stmt.iffalse.iffalse = old_iffalse
    return True


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
                children = stmt[i].iftrue.block_items
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


def req_checker(name, sem):
    req = spec[name + '_req']
    tpl = spec[name + '_tpl']
    args = []
    for elem in req:
        if elem not in sem:
            raise Exception('{0} missing'.format(elem))
        args.append(sem[elem])
    return tpl(*args)


def handle_req(ext, sem, line):
    req_type = '{0}_{1}'.format(sem['request'], sem['construct'])
    node = req_checker(req_type, sem)
    coord = Coord(0, 0)
    if req_type == 'declare_function':
        if len(ext) > 0:
            coord = Coord(last_line(ext[-1].coord) + 3, 0)
        ext.append(node)
    else:
        coord, found = find_node(ext, line, {'method': req_type, 'arg': node})
    return coord, node


def generate_code(sems, file, line):
    ast = parse_file(file, use_cpp=True)
    generator = c_generator.CGenerator()

    codes = []
    for sem in sems:
        if 'request' not in sem or 'construct' not in sem or\
           sem['request'] not in ['declare', 'add']:
            continue
        new_ext = deepcopy(ast.ext)
        coord, node = handle_req(new_ext, sem, line)
        op = generator.visit(node)
        rp = generator.visit(FileAST(new_ext))
        codes.append({'output': op, 'replace': rp, 'cursor': coord.line})
    return codes

if __name__ == '__main__':
    # codes = generate_code(
    #     [{'request': 'declare', 'construct': 'variable',
    #       'name': 'x', 'type': 'int'}],
    #     'hello.c',
    #     3
    # )
    codes = generate_code(
        [{'request': 'declare', 'construct': 'loop',
          'type': 'for'}],
        'hello.c',
        2
    )
    print(codes)
