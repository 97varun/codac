from parsing import parse_input, Grammar, Rule, Parse
from annotators import *
from operator import itemgetter


def merge_dicts(d1, d2):
     # print(d1,d2)
    if not d2:
        return d1
    result = d1.copy()
    result.update(d2)
    return result

decl_rules = [
    Rule('$ROOT', '$Declare $Declaration',
         lambda sems: merge_dicts({'request': 'declare'}, sems[1])),
    Rule('$Declare', 'declare', itemgetter(0)),
    Rule('$Declare', 'create', itemgetter(0)),
    Rule('$Declare', 'define', itemgetter(0)),
    Rule('$Declaration', '$DeclarationElement', itemgetter(0)),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(sems[0], sems[1])),
    Rule('$Declaration', '$DeclarationElement $DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(merge_dicts(sems[0], sems[1]), sems[2])),
]

dec_constructs = [
    Rule('$DeclarationElement', '$DataTypeMention', itemgetter(0)),
    Rule('$DeclarationElement', '$VariableNameMention', itemgetter(0)),
    Rule('$DeclarationElement', '$Optionals $VariableNameMention', itemgetter(1), 1.0),
    # Rule('$DeclarationElement', '$Optionals $ArrayNameMention', itemgetter(1), 1.0),
    # Rule('$DeclarationElement', '$Optionals $FuncNameMention', itemgetter(1), 1.0),
]

pack_rules = [
    Rule('$ROOT', '$Include $Inclusion', lambda sems: merge_dicts({'request': 'include'}, sems[1])),
    Rule('$Include', 'include', {}, 1.0),
    Rule('$Include', 'add', {}, 1.0),
    Rule('$Inclusion', '?$Optionals ?$PrePackName $PackName',
         lambda sems: merge_dicts(sems[2], sems[1]), 0),
    # Rule('$Inclusion', '?$Optionals ?$PrePackName $VaraibleName',
    #      lambda sems: merge_dicts({'pname' : sems[2]}, sems[1]), 0),

    # Can replace $PackageName with $variableName
    Rule('$PackName', '?$Optionals ?$Called $PackageName',
         lambda sems: merge_dicts(merge_dicts({'name': sems[2]},
          {'type': 'lib'}), {'construct': 'package'}), 2.5),
    Rule('$PackName', '?$Optionals $Called $VariableName',
         lambda sems: merge_dicts({'name': sems[2]}, {'type': 'own'}), 1.0),
    Rule('$PackName', '$VariableName',
         lambda sems: merge_dicts({'name': sems[0]}, {'type': 'own'}), 0.5),
    Rule('$PrePackName', 'library', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'package', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'library package', {'construct': 'package'}, 2.5),
    Rule('$Called', 'called', {}, 1.5),
    Rule('$Called', 'name', {}, 1.5),
]

init_rules = [
    Rule('$ROOT', '$Initialize $Initialization', lambda sems: merge_dicts({'request': 'set'}, sems[1])),
    Rule('$Initialize', 'initialize'),
    Rule('$Initialize', 'set'),
    Rule('$Initialize', 'make'),
    Rule('$Initialize', 'change'),
    Rule('$Initialize', 'update'),
    Rule('$Initialization', '$Lhs ?$Equal ?$To $Rhs', lambda sems: merge_dicts(sems[0], sems[-1])),
    Rule('$Equal', 'equal', itemgetter(0), 0.25),
    Rule('$Equal', 'equals', itemgetter(0), 0.25),
    Rule('$To', 'to', itemgetter(0), 0.25),

    Rule('$Lhs', '$Hs', lambda sems: {'lhs': sems[0]}),
    Rule('$Rhs', '$Hs', lambda sems: {'rhs': sems[0]}),
    Rule('$Rhs', '$Number', lambda sems: {'rhs': ('value', sems[0])}, 1.0),

    Rule('$Hs', '$Optionals $Hs', itemgetter(1), 0.25),
    Rule('$Hs', '$Hs $Optionals', itemgetter(0), 0.25),
    Rule('$Hs', '$Variable $VariableName', lambda sems: ('name', sems[1])),
    Rule('$Hs', '$VariableName', lambda sems: ('name', sems[0])),

    Rule('$ROOT', '$Assign $Assignment', lambda sems: merge_dicts({'request': 'set'}, sems[1])),
    Rule('$Assign', 'assign'),
    Rule('$Assignment', '$Rhs $To $Lhs', lambda sems: merge_dicts(sems[0], sems[-1])),
]

data_type_rules = [
    Rule('$DeclarationElement', '$Optionals $DataTypeMention', itemgetter(1), 1.0),
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
    Rule('$PreVariable', '$Variable', itemgetter(0), 0.0),
    Rule('$Variable', 'variable', {'construct': 'variable'}, 1.0),    
    Rule('$PreVariable', '$Called', {}, 1.0),
    Rule('$PreVariable', 'name', {}, 1.0),
]

arr_name_rules = [
    Rule('$VariableNameMention', 'array', {'construct': 'array'}, 0.5),
    Rule('$PreVariable', 'array', {'construct': 'array'}, 1.0),
]

arr_size_rules = [
    Rule('$DeclarationElement', '$Optionals $ArrSizeMention ?$DeclarationElement',
         lambda sems: merge_dicts(sems[1], sems[2]), 1.0),
    Rule('$ArrSizeMention', '?$Size $ArrSize', itemgetter(1), 0),
    Rule('$ArrSizeMention', '$Optionals $Size $ArrSize', itemgetter(2), 1.0),
    Rule('$ArrSize', '$Number', lambda sems: {'size': str(sems[0])}, 0.75),
    Rule('$ArrSize', '$Number $By $Number', lambda sems: {'size': (sems[0], sems[2])}, 1.5),
    Rule('$Size', 'size', {}, 1.0),
    Rule('$By', 'by', {}, 0.25),
    Rule('$By', 'cross', {}, 0.25),
]
# TODO : PARAMETERS
func_name_rules = [
    Rule('$ROOT', '$Declare $FnDeclaration',
         lambda sems: merge_dicts({'request': 'declare_fn'}, sems[1]), 1.0),
    Rule('$FnDeclaration', '$Function ?$PreFnName $VariableName',
         lambda sems:  merge_dicts({'name': sems[2]}, sems[0])),
    Rule('$FnDeclaration', '$FnDataTypeElement $Function ?$PreFnName $VariableName',
         lambda sems: merge_dicts(merge_dicts({'name': sems[3]}, sems[0]), sems[1]), 1.0),
    Rule('$FnDeclaration', '$Function $FnDataTypeElement ?$PreFnName $VariableName',
         lambda sems: merge_dicts(merge_dicts({'name': sems[3]}, sems[0]), sems[1]), 1.0),
    Rule('$FnDeclaration', '$Function ?$PreFnName $VariableName $FnDataTypeElement',
         lambda sems: merge_dicts(merge_dicts({'name': sems[2]}, sems[0]), sems[3]), 1.0),

    Rule('$PreFnName', '?with ?function name', {}, 1.0),
    Rule('$PreFnName', '$Called', {}, 1.0),
    Rule('$FnDataTypeElement1', '$DataTypeMention', itemgetter(0)),
    Rule('$FnDataTypeElement1', '$PreType $DataTypeMention', itemgetter(1), 1.0),
    Rule('$FnDataTypeElement', '$PreType $Returns $DataTypeMention', itemgetter(2), 2.0),
    Rule('$FnDataTypeElement', '$PreType $Returns $Optionals $DataTypeMention',
        lambda sems: sems[3], 2.0),
    Rule('$FnDataTypeElement', '$FnDataTypeElement1', itemgetter(0), 1.0),

    Rule('$Function', 'function', {'construct': 'function'}, 1.0),
    Rule('$Function', ' a function', {'construct': 'function'}, 1.5),
    Rule('$Return', 'return', {}, 1.5),
    Rule('$Return', 'return ?the value', {}, 2.5),
    Rule('$Return', 'return ?the value of', {}, 3.0),
    Rule('$Returns', 'returns', {}, 0.5),
    Rule('$Returns', '$Return', {}, 0.5),
    
]

func_call_rules = [
    Rule('$ROOT', '$FuncCall', itemgetter(0), 1.0),
    Rule('$FuncCall', '$Call ?$Optionals $Function $PreName',
         lambda sems: merge_dicts({'request': 'func_call'}, {'name': sems[3]}), 1.0),
    Rule('$FuncCall', '$Call ?$Optionals $Function $PreName $FuncCallParaElements',
         lambda sems: merge_dicts(merge_dicts({'request': 'func_call'}, {'name': sems[3]}), sems[4]), 1.5),

    Rule('$FuncCallParaElements', '$Optionals ?$Pass $Parameters $FuncCallParaElements',
         lambda sems: {'parameters': (sems[3]['parameters'])}, 1.0),
    Rule('$FuncCallParaElements', '$Optionals ?$Pass $Parameter $FuncCallParaElement',
         lambda sems: {'parameters': (sems[3])}, 1.0),
    Rule('$FuncCallParaElements', '$FuncCallParaElement $Optionals  $FuncCallParaElements',
         lambda sems: {'parameters': (sems[0], sems[2]['parameters'])}, 2.0),
    Rule('$FuncCallParaElements', '$FuncCallParaElement',
        lambda sems: {'parameters': (sems[0])}, 1.0),

 #VarName is all the variables in the current scope
    Rule('$FuncCallParaElement', '$Number', itemgetter(0), 2.0),
    Rule('$FuncCallParaElement', '$VarName', itemgetter(0), 1.0),
    Rule('$FuncCallParaElement', '$Exp', itemgetter(0), 1.0),
    Rule('$FuncCallParaElement', '$FuncCall', itemgetter(0), 1.0),

    Rule('$Call', 'call', {}, 0.5),
    Rule('$Call', 'invoke', {}, 0.5),
    Rule('$Call', 'execute', {}, 0.5),
    Rule('$Call', '$Return', {}, 0.5),
    Rule('$Pass', 'pass ?it', {}, 0.5),
    Rule('$Pass', 'give ?it', {}, 0.5),
    Rule('$Function', 'function', {}, 0.5),
]

optionals = [
    Rule('$Optionals', '$Optional ?$Optionals'),

    Rule('$Optional', '$Stopword'),
    Rule('$Optional', '$Determiner'),
    Rule('$Optional', '$Modifier'),
    Rule('$Optional', '$PreType'),

    Rule('$Modifier', 'value'),

    Rule('$Stopword', 'all'),
    Rule('$Stopword', 'as'),
    Rule('$PreType', '$Joins'),
    Rule('$PreType', 'of'),
    Rule('$Stopword', 'what'),
    Rule('$PreType', 'with'),
    # Rule('$Stopword', 'it'),
    Rule('$Stopword', 'where'),

    Rule('$Joins', 'and'),
    Rule('$Joins', 'having'),
    Rule('$Joins', 'that'),
    Rule('$Joins', 'which'),

    Rule('$Determiner', 'a'),
    Rule('$PreType', 'an'),
    Rule('$Determiner', 'the'),
]

complement = {
    '<': '>=',
    '<=': '>',
    '>': '<=',
    '>=': '<',
    '=': '!=',
}

cond_rules = [
    # Rule('$ROOT', '$Cond', lambda sems: {'cond': sems[0]}),
    # Rule('$Conds', '$Cond', lambda sems: (sems[0],)),
    Rule('$Cond', '$Cond $Conj $Cond', lambda sems: (sems[1], sems[0], sems[2])),
    Rule('$Conj', 'and', '&&', 0.25),
    Rule('$Conj', 'or', '||', 0.25),

    Rule('$Cond', 'true', ('value', 'true')),
    Rule('$Cond', 'false', ('value', 'false')),

    Rule('$Cond', '$LhsCond ?$Is $Comparator $RhsCond',
         lambda sems: (sems[2], sems[0], sems[3])),
    Rule('$Cond', '$LhsCond ?$Is $Not $Comparator $RhsCond',
         lambda sems: (complement[sems[3]], sems[0], sems[4])),
    Rule('$LhsCond', '$HsCond', itemgetter(0)),
    Rule('$Is', 'is', itemgetter(0), 0.3),
    Rule('$Not', 'not', itemgetter(0), 0.5),
    Rule('$RhsCond', '$HsCond', itemgetter(0)),

    Rule('$HsCond', '$Hs', itemgetter(0)),
    Rule('$HsCond', '$Number', lambda sems: ('value', sems[0]), 0.5),
    # Rule('$HsCond', '$Exp', lambda sems: ('value', sems[0]), 0.5),

    Rule('$Comparator', '$GreaterLess ?$Than', itemgetter(0)),
    Rule('$Comparator', '$GreaterLess ?$Than ?$Or $Equal ?$To',
         lambda sems: sems[0] + '=', 1.0),
    Rule('$Comparator', '$Equal ?$To', '='),
    Rule('$GreaterLess', '$Greater', '>', 0.5),
    Rule('$GreaterLess', '$Less', '<', 0.5),
    Rule('$Greater', 'greater'),
    Rule('$Greater', 'bigger'),
    Rule('$Less', 'less'),
    Rule('$Less', 'lesser'),
    Rule('$Less', 'smaller'),
    Rule('$Than', 'than', itemgetter(0), 0.25),
    Rule('$Or', 'or'),
]

exp_rules = [
    # Rule('$ROOT', '$Exp', lambda sems: {'exp': sems[0]}),
    Rule('$Exp', '$UnOp $Exp', lambda sems: (sems[0], sems[1])),
    Rule('$Exp', '$Exp $BinOp $Exp', lambda sems: (sems[1], sems[0], sems[2])),
    Rule('$Exp', '$Number', lambda sems: ('value', sems[0]), 0.5),
    Rule('$Exp', '?$Variable $VariableName', lambda sems: ('name', sems[1])),
    Rule('$Exp', '?$Optionals $VariableName', lambda sems: ('name', sems[1])),

    Rule('$BinOp', 'plus', '+', 0.25),
    Rule('$BinOp', 'times', '*', 0.25),
    Rule('$BinOp', 'cross', '*', 0.25),
    Rule('$BinOp', 'multiplied by', '*', 0.25),
    Rule('$BinOp', 'minus', '-', 0.25),
    Rule('$BinOp', 'by', '/', 0.25),
    Rule('$BinOp', 'divided by', '/', 0.25),
    Rule('$BinOp', 'mod', '%', 0.25),
    Rule('$BinOp', 'modulo', '%', 0.25),

    Rule('$UnOp', 'minus', '-', 0.25),
    Rule('$UnOp', 'decrement', '--', 0.25),
    Rule('$UnOp', 'minus minus', '--', 0.25),
    Rule('$UnOp', 'increment', '++', 0.25),
    Rule('$UnOp', 'plus plus', '++', 0.25),
]

ptr_rules = [
]

return_stmt_rules = [
     Rule('$ROOT', '$Return $ReturnElements',
           lambda sems: merge_dicts({'request': 'return'}, sems[1]), 1.0),
     Rule('$ReturnElements', '$ReturnElement $PreName',
           lambda sems:  merge_dicts({'name': sems[1]}, sems[0]), 2.0),
     Rule('$ReturnElements', '$Optionals $ReturnElement $PreName',
           lambda sems:  merge_dicts({'name': sems[2]}, sems[1]), 2.5),
     Rule('$ReturnElements', '$PreName',
           lambda sems: {'name': sems[0]}, 1.5),
     Rule('$ReturnElement', '$Variable', {'type': 'variable'}, 0),
     Rule('$ReturnElement', 'array', {'type': 'array'}, 0),
     Rule('$ReturnElement', 'string', {'type': 'string'}, 0),
     Rule('$ReturnElement', '$Function', {'type': 'function'}, 0),
]

dec_rules = decl_rules + dec_constructs
name_rules = var_name_rules + arr_name_rules + func_name_rules
add_param_rules = arr_size_rules

rules = dec_rules + name_rules + add_param_rules + func_call_rules + data_type_rules\
    + pack_rules + return_stmt_rules + optionals + init_rules + cond_rules + exp_rules

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
