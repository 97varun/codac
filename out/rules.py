from parsing import parse_input, Grammar, Rule, Parse
from annotators import *

def sems_0(sems):
    return sems[0]


def sems_1(sems):
    return sems[1]


def merge_dicts(d1, d2):
    if not d2:
        return d1
    result = d1.copy()
    result.update(d2)
    return result

decl_rules = [
    Rule('$ROOT', '$Declare $Declaration',
         lambda sems: merge_dicts({'request': 'declare'}, sems[1])),
    Rule('$Declare', 'declare', sems_0),
    Rule('$Declaration', '$DeclarationElement',
         sems_0),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(sems[0], sems[1])),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(merge_dicts(sems[0], sems[1]), sems[2])),
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
    Rule('$DeclarationElement', '$DataTypeMention', sems_0),
    Rule('$DeclarationElement', '$Optionals $DataTypeMention', sems_1, 1.0),
    Rule('$DataTypeMention', '$Type $DataType', lambda sems: {'type': sems[1]}, 1.0),
    Rule('$DataTypeMention', '$DataType $Type', lambda sems: {'type': sems[0]}, 1.0),
    Rule('$DataTypeMention', '$DataType', lambda sems: {'type': sems[0]}, 0.0),
    Rule('$Type', 'type'),
]

var_name_rules = [
    Rule('$DeclarationElement', '$VariableNameMention', sems_0),
    Rule('$DeclarationElement', '$Optionals $VariableNameMention', sems_1, 1.0),
    Rule('$VariableNameMention', '$VariableName', lambda sems: {'name': sems[0]}, -0.25),
    Rule('$VariableNameMention', 'variable', {'construct': 'variable'}, 0.5),
    Rule('$VariableNameMention', '$PreVariable $VariableName', lambda sems: merge_dicts({'name': sems[1]}, sems[0]), 1.0),
    Rule('$PreVariable', 'variable', {'construct': 'variable'}, 1.0),
    Rule('$PreVariable', 'called', {}, 1.0),
    Rule('$PreVariable', 'name', {}, 1.0),
]

optionals = [
    Rule('$Optionals', '$Optional ?$Optionals'),

    Rule('$Optional', '$Stopword'),
    Rule('$Optional', '$Determiner'),
    Rule('$Optional', '$Modifier'),

    Rule('$Modifier', 'value'),

    Rule('$Stopword', 'all'),
    Rule('$Stopword', 'of'),
    Rule('$Stopword', 'what'),
    Rule('$Stopword', 'with'),
    Rule('$Stopword', 'it'),

    Rule('$Determiner', 'a'),
    Rule('$Determiner', 'an'),
    Rule('$Determiner', 'the'),
]

rules = decl_rules + var_name_rules + data_type_rules + optionals + init_rules

grammar = Grammar(
    rules=rules,
    annotators=[
        DataTypeAnnotator(),
        TokenAnnotator(),
        VariableNameAnnotator(),
        NumberAnnotator()
    ]
)
