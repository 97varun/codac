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
    Rule('$Include', '$Add', {}, 1.0),
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
    Rule('$PrePackName', 'header', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'library package', {'construct': 'package'}, 2.5),
    Rule('$Add', 'add', {}, 0.0),
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
    Rule('$ArrSize', '$Number', lambda sems: {'size': (sems[0],)}, 0.75),
    Rule('$ArrSize', '$Number $By $Number', lambda sems: {'size': (sems[0], sems[2])}, 1.5),
    Rule('$Size', 'size', {}, 1.0),
    Rule('$By', 'by', {}, 0.25),
    Rule('$By', 'cross', {}, 0.25),
]
# TODO : PARAMETERS
func_name_rules = [
    Rule('$ROOT', '$Declare $FnDeclaration',
         lambda sems: merge_dicts({'request': 'declare'}, sems[1]), 1.0),
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
    Rule('$FnDataTypeElement1', '$DataTypeMention', itemgetter(0), 0.0),
    Rule('$FnDataTypeElement1', '$PreType $DataTypeMention', itemgetter(1), 1.0),
    Rule('$FnDataTypeElement', '$PreType $Returns $DataTypeMention', itemgetter(2), 2.0),
    Rule('$FnDataTypeElement', '$PreType $Returns $Optionals $DataTypeMention',
         itemgetter(3), 2.0),
    Rule('$FnDataTypeElement', '$FnDataTypeElement1', itemgetter(0), 1.0),

    Rule('$PreName', '$PreFnName $VariableName', itemgetter(1), 1.0),
    Rule('$PreName', '$VariableName', itemgetter(0), 1.0),

    Rule('$Function', 'function', {'construct': 'function'}, 1.0),
    Rule('$Function', ' a function', {'construct': 'function'}, 1.5),
    Rule('$Return', 'return', {}, 1.5),
    Rule('$Return', 'return ?the value', {}, 1.5),
    Rule('$Return', 'return ?the value of', {}, 2.0),
    Rule('$Returns', 'returns', {}, 0.5),
    Rule('$Returns', '$Return', {}, 0.5),
]

func_param_rules = [
    Rule('$ROOT', '$Add ?$Optional $FnParameterElement', itemgetter(2), 0.0),
    Rule('$FnParameterElement', '$FuncParamElement $FuncParamElement $FuncParamElement',
         lambda sems: merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), 0.0),
    Rule('$FnParameterElement', '$FuncParamElement $FuncParamElement $FuncParamElement $ParamPosElement',
         lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),
    Rule('$FnParameterElement', '$FuncParamElement $FuncParamElement $ParamPosElement $FuncParamElement',
         lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),
    Rule('$FnParameterElement', '$FuncParamElement $ParamPosElement $FuncParamElement $FuncParamElement',
         lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),

    Rule('$FuncParamElement', '$Parameter', {'construct': 'Fnparameter'}, 0.0),
    Rule('$FuncParamElement', '$PreName',
         lambda sems: {'name': sems[0]}, 0.0),
    Rule('$FuncParamElement', '$FnDataTypeElement1', itemgetter(0), 0.0),


    Rule('$ParamPosElement', '$At $Position $Number',
         lambda sems: {'position': str(sems[2])}, 1.0),
    Rule('$ParamPosElement', '$At ?$Determiner $PosNum $Position',
         lambda sems: {'position': str(sems[2])}, 1.0),
    # Rule('$FuncPositionElement', '$Number',
    #      lambda sems: {'parameter': (sems[0], sems[1]['type'], sems[3])}, 1.0),

    Rule('$Add', 'add', {}, 0.0),

    Rule('$At', 'at', {}, 1.0),
    Rule('$At', 'in', {}, 1.0),
    Rule('$Position', 'position', {}, 1.0),
    Rule('$Position', 'position number', {}, 1.5),

    Rule('$Parameter', 'parameter', {}, 1.0),
    Rule('$Parameter', 'argument', {}, 1.0),
    Rule('$Parameters', 'parameters', {}, 1.0),
    Rule('$Parameters', 'arguments', {}, 1.0),
    Rule('$Parameters', '$Parameter', {}, 0.0),
]

func_call_rules = [
    Rule('$ROOT', '$FuncCall', itemgetter(0), 0.0),
    Rule('$FuncCall', '$Call ?$Optional $Function $PreName',
         lambda sems: merge_dicts({'request': 'func_call'}, {'name': sems[3]}), 0.0),
    Rule('$FuncCall', '$Call ?$Optional $Function $PreName $FuncCallParaElements',
         lambda sems: merge_dicts(merge_dicts({'request': 'func_call'}, {'name': sems[3]}), sems[4]), 1.5),

    Rule('$FuncCallParaElements', '$Optionals ?$Pass $Parameters $FuncCallParaElements',
         lambda sems: {'parameters': (sems[3]['parameters'])}, 0.0),
    Rule('$FuncCallParaElements', '$FuncCallParaElement $Joins  $FuncCallParaElements',
         lambda sems: {'parameters': (sems[0], sems[2]['parameters'])}, 1.0),
    Rule('$FuncCallParaElements', '$FuncCallParaElement',
         lambda sems: {'parameters': (sems[0])}, 0.5),
   
    Rule('$FuncCallParaElement', '$Number', itemgetter(0), 1.0),
    Rule('$FuncCallParaElement', '$VariableName', itemgetter(0), 0.5),
    # Rule('$FuncCallParaElement', '$Exp', itemgetter(0), 0.5),
    Rule('$FuncCallParaElement', '$FuncCall', itemgetter(0), 0.5),

    Rule('$Call', 'call', {}, 0.0),
    Rule('$Call', 'invoke', {}, 0.0),
    Rule('$Call', 'execute', {}, 0.0),
    Rule('$Call', '$Return', {}, 0.5),
    Rule('$Pass', 'pass ?it', {}, 0.5),
    Rule('$Pass', 'give ?it', {}, 0.5),
    Rule('$Function', 'function', {}, 0.5),
]

add_fn_call_rules = [
    Rule('$FuncCall', '$Call ?$Optional ?$Function ?$PreFnName $FnCallName $FnCallParaElements',
         lambda sems: merge_dicts(merge_dicts({'request': 'func_call'}, {'name': sems[4]}), sems[5]), 1.5),
    Rule('$FnCallParaElements', '?$Optionals ?$Pass ?$PreString $Parameter ?$PreString $VariableName',
         lambda sems: {'parameter': sems[5]}, 1.0),
    Rule('$FnCallParaElements', '?$Optionals ?$Pass $PreString ?$Parameter ?$PreString $VariableName',
         lambda sems: {'parameter': sems[5]}, 1.0),

    Rule('$PreString', '?of ?type string ?type', {}, 0.5),
    Rule('$FnCallName', 'printf', 'printf', 1.0),
    Rule('$FnCallName', 'print f', 'printf', 1.0),
    Rule('$FnCallName', 'print', 'printf', 1.0),

]

loop_define_rules = [
    Rule('$ROOT', '$Define $Optionals $Definition',
         lambda sems: merge_dicts({'request': 'define'}, sems[2]), 0.5),
    Rule('$Define', 'define', itemgetter(0)),
    Rule('$Define', 'insert', itemgetter(0)),
    Rule('$Define', 'run', itemgetter(0)),
    Rule('$Define', 'create', itemgetter(0)),
    Rule('$Define', 'declare', itemgetter(0)),
    Rule('$Definition', '?$LoopType $Loop',
         lambda sems: merge_dicts({'construct': 'loop'}, sems[0]), 0.0),
    Rule('$LoopType', 'while', {'type': 'while'}, 0.5),
    Rule('$LoopType', 'do while', {'type': 'do while'}, 1),
    Rule('$LoopType', 'for', {'type': 'for'}, 0.5),
    Rule('$Loop', 'loop', itemgetter(0), 1),
]
#Loop Init Rules not complete (i = 0, i set to 0)
loop_init_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopInit',
         lambda sems: merge_dicts({'request': 'Append'}, sems[2]), 0.0),
    Rule('$LoopInit', '$LoopInitElement $LoopInitElement $LoopInitElement',
         lambda sems: merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), 0.0),
    # Rule('$LoopInit', '$LoopInitElement $LoopInitElement $LoopInitElement $INITIALIZATION',
    #      lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),
    # Rule('$LoopInit', '$LoopInitElement $LoopInitElement $INITIALIZATION $LoopInitElement',
    #      lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),
    # Rule('$LoopInit', '$LoopInitElement $INITIALIZATION $LoopInitElement $LoopInitElement',
    #      lambda sems: merge_dicts(merge_dicts(merge_dicts(sems[0], sems[1]), sems[2]), sems[3]), 0.0),

    Rule('$LoopInitElement', '?$Control $LoopVarNames',
        lambda sems: merge_dicts(sems[1], sems[0]), 0.0),
    Rule('$LoopInitElement', '$PreName',
         lambda sems: {'name': sems[0]}, 0.0),
    Rule('$LoopInitElement', '$FnDataTypeElement1', itemgetter(0), 0.0),

    Rule('$Control', 'control', {'construct': 'LoopInit'}, 0.5),
    Rule('$Control', '$Loop', {'construct': 'LoopInit'}, 0.5),
    Rule('$LoopVarNames', '$Variable', {}, 0.5),
    Rule('$LoopVarNames', 'initializer', {'construct': 'LoopInit'}, 0.5),
    Rule('$LoopVarNames', 'counter', {'construct': 'LoopInit'}, 0.5),
]

loop_cond_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopCond',
         lambda sems: merge_dicts({'request': 'Append'}, sems[2]), 0.0),

    Rule('$LoopCond', '?$Loop $LoopPreConds $Cond',
        lambda sems: merge_dicts({'construct': 'LoopCond'}, {'conditions': sems[2]}), 1.0),
    Rule('$LoopPreConds', 'condition', {}, 1.0),
    Rule('$LoopPreConds', 'conditions', {}, 1.0),
]

loop_update_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopUpdate',
         lambda sems: merge_dicts({'request': 'Append'}, sems[2]), 0.5),

    Rule('$LoopUpdate', '?$Loop $LoopPreUpdates $LoopUpdateElements',
         lambda sems: merge_dicts({'construct': 'LoopUpdate'}, sems[2]), 1.0),

    Rule('$LoopUpdateElements', '$Exp $Joins $LoopUpdateElements',
         lambda sems: {'updates': (sems[0], sems[2]['updates'])}, 1.5),
    # Rule('$LoopUpdateElements', '$Exp $LoopUpdateElements',
    #      lambda sems: {'updates': (sems[0], sems[1]['updates'])}, 0.0),
    Rule('$LoopUpdateElements', '$Exp',
         lambda sems: {'updates': (sems[0])}, 1.0),

    Rule('$LoopPreUpdates', '$LoopPreUpdate ?$Statement', {}, 0.0),
    Rule('$LoopPreUpdate', 'update', {}, 0.5),
    Rule('$LoopPreUpdate', 'updates', {}, 0.5),
    Rule('$LoopPreUpdate', 'modifier', {}, 0.5),
    Rule('$LoopPreUpdate', 'modifiers', {}, 0.5),
    Rule('$LoopPreUpdate', 'increment', {}, 0.5),
    Rule('$LoopPreUpdate', 'decrement', {}, 0.5),
    Rule('$LoopPreUpdate', 'step', {}, 0.5),
    Rule('$LoopPreUpdate', 'steps', {}, 0.5),
    Rule('$Statement', 'statement', {}, 0.5),
    Rule('$Statement', 'statements', {}, 0.5),
]

optionals = [
    Rule('$Optionals', '$Optional'),
    Rule('$Optionals', '$Optional $Optional'),
    Rule('$Optionals', '$Optional $Optional $Optional'),
    Rule('$Optionals', '$Optional $Optional $Optional $Optional'),

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
    Rule('$Exp', '$Exp $UnOp', lambda sems: (sems[0], sems[1])),
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
    Rule('$UnOp', 'minus minus', '--', 0.6),
    Rule('$UnOp', 'increment', '++', 0.25),
    Rule('$UnOp', 'plus plus', '++', 0.6),
]

ptr_rules = [
    Rule('$VariableNameMention', '$Pointer', {'cons': 'pointer'}, 0.5),
    Rule('$PreVariable', '$Pointer', {'cons': 'pointer'}, 1.0),
    Rule('$Pointer', 'pointer', {}, 0.0),
    Rule('$Pointer', 'points ?to', {}, 0.0),
    Rule('$Pointer', 'pointing ?to', {}, 0.0),
    Rule('$Initialize', 'point'),
]

return_stmt_rules = [
     Rule('$ROOT', '$Return $ReturnElements',
           lambda sems: merge_dicts({'request': 'return'}, sems[1]), 0.0),
     Rule('$ReturnElements', '$ReturnElement $ReturnValue',
           lambda sems: {'value': (sems[0], sems[1])}, 0.5),
     Rule('$ReturnElements', '$Optionals $ReturnElement $ReturnValue',
            lambda sems: {'value': (sems[1], sems[2])}, 1.0),
     Rule('$ReturnElements', '$PreName',
           lambda sems: {'value': ('variable', sems[0])}, 0.0),
     Rule('$ReturnElements', '$Number',
           lambda sems: {'value': ('number', sems[0])}, 1.5),
     Rule('$ReturnElements', '$Null',
           lambda sems: {'value': ('Null', 'null')}, 2.5),

     Rule('$Null', 'null', {}, 1.0),
     Rule('$ReturnValue', '$PreName', itemgetter(0), 0.0),
     Rule('$ReturnValue', '$Number', 'num', 0.5),

    #  Rule('$ReturnElement', 'value', 'value', 2.0),           
     Rule('$ReturnElement', '$Variable', 'variable', 0.0),
     Rule('$ReturnElement', 'array', 'array', 0.0),
     Rule('$ReturnElement', 'string', 'string', 0.0),
     Rule('$ReturnElement', 'expression', 'exp', 0.0),
     Rule('$ReturnElement', '$Function', 'function', 0.0),
]

rules_1 = decl_rules + dec_constructs + var_name_rules + arr_name_rules + ptr_rules
rules_2 = func_name_rules + func_param_rules + func_call_rules + add_fn_call_rules
rules_3 = loop_define_rules + loop_init_rules + loop_cond_rules + loop_update_rules 
rules_4 = pack_rules + init_rules + data_type_rules + arr_size_rules + \
         optionals + cond_rules + exp_rules + return_stmt_rules

rules = rules_1 + rules_2 + rules_3 + rules_4


grammar = Grammar(
    rules=rules,
    annotators=[
        DataTypeAnnotator(),
        TokenAnnotator(),
        VariableNameAnnotator(),
        NumberAnnotator(),
        PackageTypeAnnotator(),
        PositionalNumberAnnotator()
    ]
)
