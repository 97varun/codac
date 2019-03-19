import json

class Error():
    def __init__(self, err=''):
        self.err = err


def declare(sem):
    if 'construct' in sem:
        result = {'construct': sem['construct']}
        if sem['construct'] == 'variable':
            if 'name' not in sem:
                return Error('name')
            elif 'type' not in sem:
                return Error('type')
            else:
                result.update({'code': '{0} {1};'.format(sem['type'], sem['name'])})
        elif sem['construct'] == 'array':
            if 'name' not in sem:
                return Error('name')
            elif 'type' not in sem:
                return Error('type')
            elif 'size' not in sem:
                result.update({'code': '{0} *{1}'.format(sem['type'], sem['name'])})
            else:
                result.update({'code': '{0} {1}[{2}]'.format(sem['type'], sem['name'], ']['.join(map(str, sem['size'])))})
        elif sem['construct'] == 'function':
            if 'name' not in sem:
                return Error('name')
            elif 'type' not in sem:
                result.update({'code': '{0} {1}() {{\n\n}}'.format('void', sem['name'])})
            else:
                result.update({'code': '{0} {1}() {{\n\n}}'.format(sem['type'], sem['name'])})
        return result
    else:
        pass


def initialization(sem):
    if 'lhs' not in sem:
        return Error('lhs')
    elif 'rhs' not in sem:
        return Error('rhs')
    else:
        return {'construct': 'initialization', 'code': '{0} = {1};'.format(sem['lhs'][1], sem['rhs'][1])}


def func_call(sem):
    if 'name' not in sem:
        return Error('name')
    else:
        if 'parameters' in sem:
            p = []
            for x in sem['parameters']:
                val = []
                if isinstance(x, tuple):
                    val = [x[1]]
                elif x != 'name':
                    val = [str(x)]
                else:
                    pass
                p += val
            return {'construct': 'func_call', 'code': '{0}({1});'.format(sem['name'], (', ').join(p))}
            # else:
            #     return '#include "{0}.h"'.format(sem['name'])
        else:
                return {'construct': 'func_call', 'code': '{0}();'.format(sem['name'])}


def lib_include(sem):
    if 'name' not in sem:
        return Error('name')
    else:
        if sem['type'] == 'lib':
            return {'construct': 'include', 'code': '#include <{0}.h>'.format(sem['name'])}
        elif sem['type'] == 'own':
            return {'construct': 'include', 'code': '#include "{0}.h"'.format(sem['name'])}


def return_stmt(sem):
    if 'name' not in sem:
        return Error('name')
    else:
        return {'construct': 'return_stmt', 'code': 'return {0};'.format(sem['name'])}


def expression(sem):
    if sem[0] == 'name' or sem[0] == 'value':
        return str(sem[1])
    elif len(sem) == 2:
        return '(' + sem[0] + expression(sem[1]) + ')'
    return '(' + expression(sem[1]) + ' ' + sem[0] + ' ' + expression(sem[2]) + ')'


def condition(sem):
    if sem[0] == 'name' or sem[0] == 'value':
        return str(sem[1])
    return '(' + expression(sem[1]) + ' ' + sem[0] + ' ' + expression(sem[2]) + ')'


def generate_code(sems):
    codes = []
    for sem in sems:
        code = ''
        if 'request' in sem:
            if sem['request'] == 'declare' or sem['request'] == 'declare_fn':
                code = declare(sem)
            elif sem['request'] == 'set':
                code = initialization(sem)
            elif sem['request'] == 'func_call':
                code = func_call(sem)
            elif sem['request'] == 'include':
                code = lib_include(sem)
            elif sem['request'] == 'return':
                code = return_stmt(sem)
            
            if isinstance(code, Error):
                pass
                # print('missing %s' % code.err)
            else:
                codes.append(code)
    return codes
