from parsing import parse_input, Grammar, Rule, Parse
from annotators import *

def sems_0(sems):
    return sems[0]


def sems_1(sems):
    return sems[1]

def sems_2(sems):
    return sems[2]

def sems_3(sems):
    return sems[3]

def merge_dicts(d1, d2):
    # print(d1, d2)
    if not d2:
        return d1
    result = d1.copy()
    result.update(d2)
    return result

decl_rules = [
    Rule('$ROOT', '$Declare $Declaration',
         lambda sems: merge_dicts({'request': 'declare'}, sems[1])),
    Rule('$Declare', 'declare', sems_0),
    Rule('$Declare', 'create', sems_0),
    Rule('$Declare', 'define', sems_0),
    Rule('$Declaration', '$DeclarationElement', sems_0),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(sems[0], sems[1])),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(merge_dicts(sems[0], sems[1]), sems[2])),
]

dec_constructs = [
    Rule('$DeclarationElement', '$DataTypeMention', sems_0),
    Rule('$DeclarationElement', '$VariableNameMention', sems_0),
    Rule('$DeclarationElement', '$Optionals $VariableNameMention', sems_1, 1.0),
    # Rule('$DeclarationElement', '$Optionals $ArrayNameMention', sems_1, 1.0),
    # Rule('$DeclarationElement', '$Optionals $FuncNameMention', sems_1, 1.0),

]

pack_rules = [
    Rule('$ROOT', '$Include $Inclusion', lambda sems: merge_dicts({'request': 'include'}, sems[1])),
    Rule('$Include', 'include', 5.0),
    Rule('$Include', 'add', 5.0),
    Rule('$Inclusion', '?$Optionals ?$PrePackName $PackName',
         lambda sems: merge_dicts(sems[2], sems[1]), 0),
 
 #Can replace $PackageName with $variableName
    Rule('$PackName', '?$Optionals ?$Called $PackageName', lambda sems:  {'name': sems[2]}, 0.5),
    Rule('$PrePackName', 'library', {'construct': 'package'}, 0.5),
    Rule('$PrePackName', 'package', {'construct': 'package'}, 0.5),
    Rule('$PrePackName', 'library package', {'construct': 'package'}, 1.2),
    Rule('$Called', 'called'),
    Rule('$Called', 'name'),
]

loop_rules = [
    Rule('$ROOT', '$Define $Optionals $Definition',
         lambda sems: merge_dicts({'request': 'define'}, sems[2]), 0),
    Rule('$Define', 'define', sems_0),
    Rule('$Define', 'insert', sems_0),
    # Rule('$Define', 'make', sems_0),              USED FOR INITIALIZATION
    Rule('$Define', 'run', sems_0),
    Rule('$Define', 'create', sems_0),
    Rule('$Define', 'declare', sems_0),
    Rule('$Definition', '?$LoopType $Loop ?$VariableName',
         lambda sems: merge_dicts({'construct': 'loop'}, sems[0]), 1.0),
    Rule('$LoopType', 'while', {'type': 'while'}, 1),
    Rule('$LoopType', 'do while', {'type': 'do while'}, 2),
    Rule('$LoopType', 'for', {'type': 'for'}, 1),
    Rule('$Loop', 'loop', sems_0, 2),
]

init_rules = [
    Rule('$ROOT', '$Initialize $Initialization', lambda sems: merge_dicts({'request': 'set'}, sems[1])),
    Rule('$Initialize', 'initialize'),
    Rule('$Initialize', 'set'),
    Rule('$Initialize', 'make'),
    Rule('$Initialize', 'change'),
    Rule('$Initialize', 'update'),
    Rule('$Initialization', '$Lhs ?$Equal ?$To $Rhs', lambda sems: merge_dicts(sems[0], sems[-1])),
    Rule('$Equal', 'equal'),
    Rule('$Equal', 'equals'),
    Rule('$To', 'to'),

    Rule('$Lhs', '$Hs', lambda sems: {'lhs': sems[0]}),
    Rule('$Rhs', '$Hs', lambda sems: {'rhs': sems[0]}),
    Rule('$Rhs', '$Number', lambda sems: {'rhs': {'value': sems[0]}}),

    Rule('$Hs', '$Optionals $Hs', sems_1),
    Rule('$Hs', '$Hs $Optionals', sems_0),
    Rule('$Hs', '$Variable $VariableName', lambda sems: {'name': sems[1]}), 
    Rule('$Variable', 'variable'),
    Rule('$Hs', '$VariableName', lambda sems: {'name': sems[0]}),
]

data_type_rules = [
    Rule('$DeclarationElement', '$Optionals $DataTypeMention', sems_1, 1.0),
    Rule('$DataTypeMention', '$Type ?$Optionals $DataType', lambda sems: {'type': sems[2]}, 1.0),
    Rule('$DataTypeMention', '$DataType $Type', lambda sems: {'type': sems[0]}, 1.0),
    Rule('$DataTypeMention', '$DataType', lambda sems: {'type': sems[0]}, 0.0),
    Rule('$Type', 'type'),
]

var_name_rules = [
    Rule('$VariableNameMention', '$VariableName', lambda sems: {'name': sems[0]}, -0.25),
    Rule('$VariableNameMention', 'variable', {'construct': 'variable'}, 0.5),
    Rule('$VariableNameMention', '$PreVariable $VariableName',
         lambda sems: merge_dicts({'name': sems[1]}, sems[0]), 1.0),
    Rule('$VariableNameMention', '$PreVariable $PreVariable $VariableName',
         lambda sems: merge_dicts(merge_dicts({'name': sems[2]}, sems[0]), sems[1]), 1.7),
    Rule('$PreVariable', 'variable', {'construct': 'variable'}, 1.0),
    Rule('$PreVariable', 'called', {}, 1.0),
    Rule('$PreVariable', 'name', {}, 1.0),
]

arr_name_rules = [
    Rule('$VariableNameMention', 'array', {'construct': 'array'}, 0.5),
    Rule('$PreVariable', 'array', {'construct': 'array'}, 1.0),
]

arr_size_rules = [
    Rule('$DeclarationElement', '$Optionals $ArrSizeMention ?$DeclarationElement',
         lambda sems: merge_dicts(sems[1], sems[2]), 1.0),
    Rule('$ArrSizeMention', '?$Size $ArrSize', sems_1, 0),
    Rule('$ArrSizeMention', '$Optionals $Size $ArrSize', sems_2, 1.0),
    Rule('$ArrSize', '$Number', lambda sems: {'size': str(sems[0])}, 0.75),
    Rule('$ArrSize', '$Number $By $Number', lambda sems: {'size': (sems[0], sems[2])}, 1.5),
    Rule('$Size', 'size', 1.0),
    Rule('$By', 'by', 0.25),
    Rule('$By', 'cross', 0.25),

]
# TODO : PARAMETERS
func_name_rules = [
    Rule('$DeclarationElement', '$Optionals $Return ?$Optionals $DataTypeMention', sems_3, 2.0),
    Rule('$VariableNameMention', 'function', {'construct': 'function'}, 0.5),
    Rule('$PreVariable', 'function', {'construct': 'function'}, 1.0),
    Rule('$Return', 'return', 0.5)
]


optionals = [
    Rule('$Optionals', '$Optional ?$Optionals'),

    Rule('$Optional', '$Stopword'),
    Rule('$Optional', '$Determiner'),
    Rule('$Optional', '$Modifier'),

    Rule('$Modifier', 'value'),

    Rule('$Stopword', 'and'),
    Rule('$Stopword', 'all'),
    Rule('$Stopword', 'of'),
    Rule('$Stopword', 'what'),
    Rule('$Stopword', 'with'),
    Rule('$Stopword', 'it'),

    Rule('$Determiner', 'a'),
    Rule('$Determiner', 'an'),
    Rule('$Determiner', 'the'),
]


dec_rules = decl_rules + dec_constructs
name_rules = var_name_rules + arr_name_rules + func_name_rules 
rules = dec_rules + name_rules + data_type_rules + arr_size_rules + pack_rules + loop_rules  + optionals + init_rules


grammar = Grammar(
    rules=rules,
    annotators=[
        DataTypeAnnotator(),
        TokenAnnotator(),
        VariableNameAnnotator(),
        NumberAnnotator(),
        PackageTypeAnnotator()
    ]
)
