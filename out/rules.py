from parsing import parse_input, Grammar, Rule, Parse
from annotators import *
from operator import itemgetter


def merge_dicts(*dicts):
    result = dict()
    for dct in dicts:
        if not dct:
            continue
        result.update(dct)
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
    Rule('$Declaration',
         '$DeclarationElement $DeclarationElement $DeclarationElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2])),
    Rule('$Declaration',
         '$DeclarationElement $DeclarationElement $DeclarationElement\
          $DeclarationElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2], sems[3])),
]

dec_constructs = [
    Rule('$DeclarationElement', '$DataTypeMention', itemgetter(0)),
    Rule('$DeclarationElement', '$VariableNameMention', itemgetter(0)),
    Rule('$DeclarationElement', '$InitElement', itemgetter(0)),
    Rule('$DeclarationElement', '$PreVariable', itemgetter(0)),
    Rule('$DataTypeMention', '$Optionals $DataTypeMention',
         itemgetter(1), 0.25),
    Rule('$VariableNameMention', '$Optionals $VariableNameMention',
         itemgetter(1), 0.25),
    Rule('$InitElement', '$Optionals $InitElement', itemgetter(1), 0.25),
    Rule('$PreVariable', '$Optionals $PreVariable', itemgetter(1), 0.25),
]

pack_rules = [
    Rule('$ROOT', '$Include $Inclusion',
         lambda sems: merge_dicts({'request': 'include'}, sems[1])),
    Rule('$Include', 'include', {}, 1.0),
    Rule('$Inclusion', '?$Optionals ?$PrePackName $PackName',
         lambda sems: merge_dicts(sems[2], sems[1]), 0),
    # Can replace $PackageName with $variableName
    Rule('$PackName', '?$Optionals ?$Called $PackageName',
         lambda sems: merge_dicts(
             {'name': sems[2]}, {'type': 'lib', 'construct': 'package'}), 2.5),
    Rule('$PackName', '?$Optionals $Called $VariableName',
         lambda sems: merge_dicts(sems[2], {'type': 'own'}), 1.0),
    Rule('$PackName', '$VariableName',
         lambda sems: merge_dicts(sems[0], {'type': 'own'}), 0.5),
    Rule('$PrePackName', 'library', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'package', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'header', {'construct': 'package'}, 1.0),
    Rule('$PrePackName', 'library package', {'construct': 'package'}, 2.5),
    Rule('$Add', 'add', {}, 0.0),
    Rule('$Called', 'called', {}, 1.5),
    Rule('$Called', 'name', {}, 1.5),
]

init_rules = [
    Rule('$ROOT', '$Initialize $Initialization',
         lambda sems: merge_dicts({'request': 'declare',
                                   'construct': 'assignment'}, sems[1])),
    Rule('$Initialize', 'initialize'),
    Rule('$Initialize', 'set'),
    Rule('$Initialize', 'make'),
    Rule('$Initialization', '$Lhs ?$Equal ?$To ?$Rhs',
         lambda sems: merge_dicts(sems[0], sems[-1])),
    Rule('$Equal', 'equal', itemgetter(0), 0.25),
    Rule('$Equal', 'equals', itemgetter(0), 0.25),
    Rule('$To', 'to', itemgetter(0), 0.5),

    Rule('$Lhs', '$Hs', lambda sems: {'lhs': sems[0]}),
    Rule('$Rhs', '$Exp', lambda sems: {'rhs': sems[0]}),

    Rule('$Hs', '$Optionals $Hs', itemgetter(1), 0.25),
    Rule('$Hs', '$Hs $Optionals', itemgetter(0), 0.25),
    Rule('$Hs', '$VariableName', lambda sems: ('name', sems[0]['name'])),
    Rule('$Hs', '$ArrRef', itemgetter(0), 0.25),

    Rule('$ROOT', '$Assign $Assignment',
         lambda sems: merge_dicts({'request': 'declare',
                                   'construct': 'assignment'}, sems[1])),
    Rule('$Assign', 'assign'),
    Rule('$Assignment', '$Rhs $To $Lhs',
         lambda sems: merge_dicts(sems[0], sems[-1])),
]

data_type_rules = [
    Rule('$DataTypeMention', '$Type ?$Optionals $DataType',
         lambda sems: {'type': sems[2]}, 1.0),
    Rule('$DataTypeMention', '$DataType $Type',
         lambda sems: {'type': sems[0]}, 1.0),
    Rule('$DataTypeMention', '$DataType', lambda sems: {'type': sems[0]}),
    Rule('$Type', 'type', {}, 0.1),
    Rule('$DataTypeMention', '$To $DataTypeMention', itemgetter(1)),

    # pointer types
    Rule('$DataTypeMention', '$Pointer $To $DataTypeMention',
         lambda sems: {'type': sems[2]['type'], 'modifier': 'pointer'}),
    Rule('$DataTypeMention', '$DataTypeMention $Pointer',
         lambda sems: {'type': sems[0]['type'], 'modifier': 'pointer'}),
    Rule('$Pointer', 'pointer', {}, 0.5),
    Rule('$Pointer', 'pointing', {}, 0.5),
    Rule('$Pointer', 'points', {}, 0.5),

    # data types
    Rule('$DataType', '$Integer', 'int'),
    Rule('$DataType', '$Short', 'short'),
    Rule('$DataType', '$Short $Integer', 'short int', 0.25),
    Rule('$DataType', 'long', 'long'),
    Rule('$DataType', '$Long $Integer', 'long int', 0.25),
    Rule('$DataType', 'long double', 'int'),
    Rule('$DataType', 'long long', 'int'),
    Rule('$DataType', '$Long $Long $Integer', 'int', 0.5),
    Rule('$DataType', 'char', 'char'),
    Rule('$DataType', 'character', 'char'),
    Rule('$DataType', 'double', 'double'),
    Rule('$DataType', 'float', 'float'),
    Rule('$Integer', 'int', {}),
    Rule('$Integer', 'integer', {}),
    Rule('$Short', 'short', {}),
    Rule('$Long', 'long', {})
]

var_name_rules = [
    Rule('$VariableNameMention', '$VariableName',
         itemgetter(0), 0.0),
    Rule('$VariableName', '$DataTypeMention $VarName',
         lambda sems: merge_dicts(sems[0], {'name': sems[1]}), 0.25),
    Rule('$VariableName', '$PreVariable $VarName',
         lambda sems: merge_dicts(sems[0], {'name': sems[1]}), 0.25),
    Rule('$VariableName', '$PreVariable $PreVariable $VarName',
         lambda sems: merge_dicts(sems[0], sems[1], {'name': sems[2]}), 1.0),
    Rule('$VariableName', '$ScopeVariable', lambda sems: {'name': sems[0]}),
    Rule('$PreVariable', 'variable', {'construct': 'variable'}, 0.5),
    Rule('$PreVariable', 'parameter', {'construct': 'variable'}, 0.5),
    Rule('$PreVariable', 'function', {'construct': 'function'}, 0.5),
    Rule('$PreVariable', 'array', {'construct': 'array'}, 0.5),
    Rule('$PreVariable', 'package', {'construct': 'package'}, 0.5),
    Rule('$PreVariable', 'index', {}, 0.5),
    Rule('$PreVariable', 'pointer', {'modifier': 'pointer'}, 0.5),
    Rule('$PreVariable', 'called', {}, 0.5),
    Rule('$PreVariable', 'name', {}, 0.5),
    Rule('$PreVariable', '$PrePackName', {'construct': 'package'}, 0.5),
    Rule('$Variable', 'variable', {}),
]

arr_size_rules = [
    Rule('$DeclarationElement',
         '$Optionals $ArrSizeMention ?$DeclarationElement',
         lambda sems: merge_dicts(sems[1], sems[2]), 1.0),
    Rule('$DeclarationElement',
         '?$DeclarationElement $Optionals $ArrSizeMention',
         lambda sems: merge_dicts(sems[2], sems[0]), 1.0),
    Rule('$ArrSizeMention', '?$Size $ArrSize', itemgetter(1), 0),
    Rule('$ArrSizeMention', '$Optionals $Size $ArrSize', itemgetter(2), 1.0),
    Rule('$ArrSize', '$Number', lambda sems: {'size': (sems[0],)}, 0.75),
    Rule('$ArrSize', '$Number $By $Number',
         lambda sems: {'size': (sems[0], sems[2])}, 1.5),
    Rule('$Size', 'size', {}, 1.0),
    Rule('$By', 'by', {}, 0.25),
    Rule('$By', 'cross', {}, 0.25),
]

func_name_rules = [
    Rule('$ROOT', '$Declare $FnDeclaration',
         lambda sems: merge_dicts({'request': 'declare'}, sems[1]), 1.0),
    Rule('$FnDeclaration', '$Function ?$PreFnName $VariableName',
         lambda sems:  merge_dicts(sems[2], sems[0])),
    Rule('$FnDeclaration',
         '$FnDataTypeElement $Function ?$PreFnName $VariableName',
         lambda sems: merge_dicts(sems[3], sems[0], sems[1]), 1.0),
    Rule('$FnDeclaration',
         '$Function $FnDataTypeElement ?$PreFnName $VariableName',
         lambda sems: merge_dicts(sems[3], sems[0], sems[1]), 1.0),
    Rule('$FnDeclaration',
         '$Function ?$PreFnName $VariableName $FnDataTypeElement',
         lambda sems: merge_dicts(sems[2], sems[0], sems[3]), 1.0),

    Rule('$PreFnName', '?with ?function name', {}, 1.0),
    Rule('$PreFnName', '$Called', {}, 1.0),
    Rule('$FnDataTypeElement1', '$DataTypeMention', itemgetter(0), 0.0),
    Rule('$FnDataTypeElement1', '$PreType $DataTypeMention',
         itemgetter(1), 1.0),
    Rule('$FnDataTypeElement', '$PreType $Returns $DataTypeMention',
         itemgetter(2), 2.0),
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
    Rule('$ROOT', '$Add ?$Optional $FnParameterElement',
         lambda sems: merge_dicts(sems[2], {'request': 'add'}), 0.0),
    Rule('$FnParameterElement',
         '$FuncParamElement $FuncParamElement $FuncParamElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2]), 0.0),
    Rule('$FnParameterElement',
         '$FuncParamElement $FuncParamElement $FuncParamElement\
              $ParamPosElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2], sems[3]), 0.0),
    Rule('$FnParameterElement',
         '$FuncParamElement $FuncParamElement $ParamPosElement\
              $FuncParamElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2], sems[3]), 0.0),
    Rule('$FnParameterElement',
         '$FuncParamElement $ParamPosElement $FuncParamElement\
              $FuncParamElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2], sems[3]), 0.0),

    Rule('$FuncParamElement', '$Parameter', {'construct': 'parameter'}, 0.0),
    Rule('$FuncParamElement', '$VariableNameMention',
         lambda sems: {'name': sems[0]['name']}, 0.0),
    Rule('$FuncParamElement', '$FnDataTypeElement1', itemgetter(0), 0.0),


    Rule('$ParamPosElement', '$At $Position $Number',
         lambda sems: {'position': sems[2]}, 1.0),
    Rule('$ParamPosElement', '$At ?$Determiner $PosNum $Position',
         lambda sems: {'position': sems[2]}, 1.0),

    Rule('$Add', 'add', {}, 0.0),
    Rule('$At', 'at', {}, 1.0),
    Rule('$At', 'in', {}, 1.0),
    Rule('$Position', 'position', {}, 1.0),
    Rule('$Position', 'position number', {}, 1.5),

    Rule('$Parameters', 'parameters', {}, 1.0),
    Rule('$Parameters', 'arguments', {}, 1.0),
    Rule('$Parameters', '$Parameter', {}, 0.0),
    Rule('$Parameter', 'parameter', {}, 1.0),
    Rule('$Parameter', 'argument', {}, 1.0),
]

func_call_rules = [
    Rule('$ROOT', '$FuncCall',
         lambda sems: merge_dicts(sems[0], {'request': 'declare'}), 0.0),
    Rule('$FuncCall',
         '$Call ?$Optional $PreName ?$FuncCallParaElements',
         lambda sems: merge_dicts(
            {'construct': 'func_call', 'name': sems[2]['name']},
            sems[3]), 1.5),

    Rule('$FuncCallParaElements',
         '$Optionals ?$Pass $Parameters $FuncCallParaElements',
         lambda sems: {'parameters': (*sems[3]['parameters'],)}, 0.0),
    Rule('$FuncCallParaElements',
         '$FuncCallParaElement ?$Joins $FuncCallParaElements',
         lambda sems: {'parameters': (sems[0], *sems[2]['parameters'])}, 1.0),
    Rule('$FuncCallParaElements', '$FuncCallParaElement',
         lambda sems: {'parameters': (sems[0],)}, 0.5),

    Rule('$FuncCallParaElement', '$Exp', itemgetter(0), 0.5),
    Rule('$FuncCallParaElement', '$FuncCall', itemgetter(0), 0.5),

    Rule('$Call', 'call', {}, 0.0),
    Rule('$Call', 'invoke', {}, 0.0),
    Rule('$Call', 'execute', {}, 0.0),
    # Rule('$Call', '$Return', {}, 0.5),
    Rule('$Pass', 'pass ?it', {}, 0.5),
    Rule('$Pass', 'give ?it', {}, 0.5),
    Rule('$Function', 'function', {}, 0.5),
]

add_fn_call_rules = [
    Rule('$ROOT',
         '$Call ?$Optional ?$Function ?$PreFnName $FnCallType\
              $FnCallParaElements',
         lambda sems: merge_dicts(
             {'request': 'declare', 'construct': 'func_call', 'name': sems[4]},
             sems[5]), 1.5),
    Rule('$FnCallParaElements',
         '?$Optionals ?$Pass ?$PreString $Parameters ?$PreString\
              $FuncParameter',
         itemgetter(5), 1.0),
    Rule('$FnCallParaElements', '?$Optionals ?$Pass $PreString $FuncParameter',
         itemgetter(3), 1.0),
    Rule('$FuncParameter',
         '$StringText $Joins ?$Parameter $Exp',
         lambda sems: {'parameters': (('str', sems[0]), sems[3])}, 1.0),
    Rule('$FuncParameter',
         '$StringText $Joins $FnDataTypeElement1 ?$Parameter $Exp',
         lambda sems: {'parameters': (('str', sems[0]), sems[4])}, 1.0),
    Rule('$FuncParameter', '$StringText',
         lambda sems: {'parameters': (('str', sems[0]),)}, 0.5),
    
    Rule('$PreString', '?$Optional ?$Type $String ?$Type ?$PreFnName', {}, 1.0),
    Rule('$FnCallType', 'printf', 'printf', 1.5),
    Rule('$FnCallType', 'print f', 'printf', 1.5),
    Rule('$FnCallType', 'print', 'printf', 1.5),
    Rule('$FnCallType', 'scanf', 'scanf', 1.5),
    Rule('$FnCallType', 'scan f', 'scanf', 1.5),
    Rule('$Mod', 'mod', {}, 0),
    Rule('$Mod', 'modulus', {}, 0),
    Rule('$String', 'string', {}, 0),
]

loop_define_rules = [
    Rule('$ROOT', '$Define ?$Optionals $Definition',
         lambda sems: merge_dicts({'request': 'declare'}, sems[2]), 0.5),
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

loop_init_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopInit',
         lambda sems: merge_dicts({'request': 'add'}, sems[2]), 0.0),
    Rule('$LoopInit', '$LoopInitElement $LoopInitElement $LoopInitElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2]), 0.0),
    Rule('$LoopInit', '$LoopInitElement $LoopInitElement $LoopInitElement\
         $LoopInitElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2], sems[3]), 0.0),

    Rule('$LoopInitElement', '?$Control $LoopVarNames',
         lambda sems: merge_dicts(
             sems[1], sems[0], {'construct': 'init'}), 0.5),
    Rule('$LoopInitElement', '$VariableName',
         lambda sems: {'name': sems[0]['name']}, 0.0),
    Rule('$LoopInitElement', '$DataTypeMention', itemgetter(0), 0.5),

    # for initializing loop variables and variable declarations
    Rule('$LoopInitElement', '$InitElement', itemgetter(0)),
    Rule('$InitElement', '$Equal ?$To $Exp',
         lambda sems: {'value': sems[2]}, 0.5),
    Rule('$InitElement', '$Optional $Modifier $Exp',
         lambda sems: {'value': sems[1]}, 0.5),
    Rule('$Equal', 'initialize', {}, 0.25),
    Rule('$Equal', 'initialized', {}, 0.25),
    Rule('$Equal', 'set', {}, 0.25),

    Rule('$Control', 'control', {}, 0.5),
    Rule('$Control', '$Loop', {}, 0.5),
    Rule('$LoopVarNames', '$Variable', {}, 0.5),
    Rule('$LoopVarNames', 'initializer', {}, 0.5),
    Rule('$LoopVarNames', 'counter', {}, 0.5),
]

loop_cond_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopCond',
         lambda sems: merge_dicts(
             {'request': 'add'}, sems[2]), 0.0),
    Rule('$LoopCond', '?$Loop $LoopPreConds $Cond',
         lambda sems: {'construct': 'condition', 'cond': sems[2]}, 1.0),
    Rule('$LoopPreConds', 'condition', {}, 1.0),
    Rule('$LoopPreConds', 'conditions', {}, 1.0),
]

loop_update_rules = [
    Rule('$ROOT', '$Add ?$Optional $LoopUpdate',
         lambda sems: merge_dicts({'request': 'add'}, sems[2]), 0.5),

    Rule('$LoopUpdate', '?$Loop $LoopPreUpdates $LoopUpdateElements',
         lambda sems: merge_dicts({'construct': 'update'}, sems[2]), 1.0),

    # Rule('$LoopUpdateElements', '$Exp $Joins $LoopUpdateElements',
    #      lambda sems: {'updates': (sems[0], sems[2]['updates'])}, 1.5),
    # Rule('$LoopUpdateElements', '$Exp $LoopUpdateElements',
    #      lambda sems: {'updates': (sems[0], sems[1]['updates'])}, 0.0),
    Rule('$LoopUpdateElements', '$Exp',
         lambda sems: {'updates': sems[0]}, 1.0),

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
    '==': '!=',
}

cond_rules = [
    Rule('$ROOT', '$Cond', lambda sems: {'cond': sems[0]}),
    Rule('$Cond', '$Cond $Conj $Cond',
         lambda sems: (sems[1], sems[0], sems[2])),
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

    Rule('$HsCond', '$Exp', itemgetter(0), 0.5),

    Rule('$Comparator', '$GreaterLess ?$Than', itemgetter(0)),
    Rule('$Comparator', '$GreaterLess ?$Than ?$Or $Equal ?$To',
         lambda sems: sems[0] + '=', 1.0),
    Rule('$Comparator', '$Equal ?$To', '=='),
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
    Rule('$ROOT', '$Exp', lambda sems: {'exp': sems[0]}),
    Rule('$Exp', '$UnOp $Exp', lambda sems: (sems[0], sems[1])),
    Rule('$Exp', '$Exp $UnOp', lambda sems: ('p' + sems[1], sems[0])),
    Rule('$Exp', '$Exp $BinOp $Exp', lambda sems: (sems[1], sems[0], sems[2])),
    Rule('$Exp', '$Number', lambda sems: ('value', sems[0]), 0.5),
    Rule('$Exp', '$VariableName', lambda sems: ('name', sems[0]['name'])),

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
    Rule('$UnOp', 'address ?of', '&', 0.25),
    Rule('$UnOp', 'value at address', '*', 0.25),
    Rule('$UnOp', 'dereference', '*', 0.25),
]

ptr_rules = [
    # Rule('$VariableNameMention', '$Pointer',
    #      {'construct': 'pointer'}, 0.5),
    # Rule('$PreVariable', '$Pointer',
    #      {'construct': 'pointer'}, 1.0),
    # Rule('$Pointer', 'pointer', {}, 0.0),
    # Rule('$Pointer', 'points ?to', {}, 0.0),
    # Rule('$Pointer', 'pointing to', {}, 0.0),
    # Rule('$Initialize', 'point'),
]

return_stmt_rules = [
    Rule('$ROOT', '$Return $ReturnElements',
         lambda sems: merge_dicts(
             {'request': 'declare', 'construct': 'return'}, sems[1]), 0),
    Rule('$ReturnElements', '$ReturnElement $ReturnValue',
         lambda sems: merge_dicts(sems[0], sems[1]), 0.5),
    Rule('$ReturnElements', '$Optionals $ReturnElement $ReturnValue',
         lambda sems: merge_dicts(sems[1], sems[2]), 1.0),
    Rule('$ReturnElements', '$ReturnValue', itemgetter(0), 0),

    Rule('$ReturnElements', '$Optionals $ReturnFuncElement $ReturnValue',
         lambda sems: merge_dicts(sems[1], {'value': (sems[2]['value'][0],
                                            sems[2]['value'][1] + '()')}), 1.0),

    Rule('$ReturnElements', '$Null',
         lambda sems: {'value': ('value', 'null')}, 2.5),

    Rule('$ReturnValue', '$PreFnName $Exp',
         lambda sems: {'value': sems[1]}, 1.0),
    Rule('$ReturnValue', '$Exp',
         lambda sems: {'value': sems[0]}, 0),

    Rule('$ReturnElement', '$Variable', 0.0),
    Rule('$ReturnElement', 'array', 0.0),
    Rule('$ReturnElement', 'string', 0.0),
    Rule('$ReturnElement', 'expression', 0.0),
    Rule('$ReturnFuncElement', '$Function', 0.0),

    Rule('$Null', 'null', {}, 1.0),
]

if_rules = [
     Rule('$ROOT', '$Declare ?$Optionals $IfElseStatement',
          lambda sems: merge_dicts({'request': 'declare'}, sems[2])),
     Rule('$IfElseStatement', '$If ?$Statement', {'construct': 'if'}),
     Rule('$IfElseStatement', '$If $Else ?$Statement',
          {'construct': 'if_else'}),
     Rule('$IfElseStatement', '$Conditional ?$Statement', {'construct': 'if'}),
     Rule('$If', 'if', {}, 0.75),
     Rule('$Else', 'else', {}, 0.75),
     Rule('$Statement', 'statement', {}, 0.25),
     Rule('$Statement', 'block', {}, 0.25),
     Rule('$Conditional', 'conditional', {}, 0.25),

     # rules to add conditions, else if, else
     Rule('$ROOT', '$Add ?$Optionals $Condition $Cond',
          lambda sems: {'request': 'add', 'cond': sems[3],
                        'construct': 'condition'}),
     Rule('$ROOT', '$Add ?$Optionals $ElseIf ?$Statement',
          lambda sems: merge_dicts({'request': 'add'}, sems[2])),
     Rule('$ElseIf', '$Else', {'construct': 'else'}),
     Rule('$ElseIf', '$Else $If', {'construct': 'else_if'}),
     Rule('$Add', 'add'),
     Rule('$Condition', 'condition', {}),
]

nav_rules = [
    Rule('$ROOT', '$Nav ?$Determiner $NavElements',
         lambda sems: merge_dicts({'request': 'navigate'}, sems[2]), 0.0),
    Rule('$NavElements', '$NavElement $NavElement ?$NavElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2]), 0.0),
    Rule('$NavElements', '$SpecialElems $VariableName',
         lambda sems: merge_dicts(sems[0], {'name': sems[1]['name']}), 0.0),

    Rule('$NavElement', '$JumpType', itemgetter(0), 1.0),
    Rule('$NavElement', '$JumpDirection', itemgetter(0), 1.0),
    Rule('$NavElement', '$JumpAmount', itemgetter(0), 1.0),

    Rule('$JumpType', '$Line', {'construct': 'line'}, 0),
    Rule('$JumpType', '$Place', {'construct': 'character'}, 0),
    Rule('$JumpType', '$SpecialElems', itemgetter(0), 0),
    Rule('$SpecialElems', 'function', {'construct': 'function'}, 0),
    Rule('$SpecialElems', 'loop', {'construct': 'loop'}, 0),
    Rule('$SpecialElems', 'variable', {'construct': 'variable'}, 0),

    Rule('$JumpDirection', 'up', {'direction': 'up'}, 0),
    Rule('$JumpDirection', 'down', {'direction': 'down'}, 0),
    Rule('$JumpDirection', 'left', {'direction': 'left'}, 0),
    Rule('$JumpDirection', 'right', {'direction': 'right'}, 0),
    Rule('$JumpDirection', 'previous', {'direction': 'back'}, 0),
    Rule('$JumpDirection', 'next', {'direction': 'next'}, 0),
    Rule('$JumpDirection', 'back', {'direction': 'back'}, 0),
    Rule('$JumpDirection', 'front', {'direction': 'next'}, 0),
    Rule('$JumpDirection', 'end ?of', {'direction': 'end'}, 0),
    Rule('$JumpDirection', 'start ?of', {'direction': 'start'}, 0),
    Rule('$JumpDirection', 'inner', {'direction': 'inner'}, 0),
    Rule('$JumpDirection', 'outer', {'direction': 'outer'}, 0),
    Rule('$JumpDirection', 'current', {'direction': 'current'}, 0),

    Rule('$JumpAmount', '?$Num $NumType', itemgetter(1), 0),

    Rule('$Nav', 'go ?to', {}, 1.0),
    Rule('$Nav', 'goto', {}, 1.0),
    Rule('$Num', 'number', {}, 0.5),
    Rule('$Num', 'numbers', {}, 0.5),

    Rule('$NumType', '$Number', lambda sems: {'value': sems[0]}, 0.5),
    Rule('$NumType', '$PosNum', lambda sems: {'value': sems[0]}, 0.5),

    Rule('$Line', 'line', {}, 0),
    Rule('$Line', 'lines', {}, 0),
    Rule('$Place', 'place', {}, 0),
    Rule('$Place', 'places', {}, 0),
    Rule('$Place', 'position', {}, 0),
    Rule('$Place', 'positions', {}, 0),
    Rule('$Place', 'character', {}, 0),
    Rule('$Place', 'characters', {}, 0),
]

edit_rules = [
    Rule('$ROOT', '$EditElements',
         lambda sems: merge_dicts({'request': 'edit'}, sems[0])),
    Rule('$EditElements', '$EditType ?$EditParams',
         lambda sems: merge_dicts(sems[0], sems[1]), 0.0),
    Rule('$EditElements', '$Change $Initialization',
         lambda sems: merge_dicts(sems[0], sems[1])),

    Rule('$EditParams', '$EditElement $EditElement ?$EditElement',
         lambda sems: merge_dicts(sems[0], sems[1], sems[2]), 0.0),
    Rule('$EditParams', '$SpecialElems $VariableName',
         lambda sems: merge_dicts(
             {'e_type': sems[0]['construct']},
             {'name': sems[1]['name']}), 0.0),

    Rule('$EditElement', '$JumpType',
         lambda sems: {'e_type': sems[0]['construct']}, 1.0),
    Rule('$EditElement', '$JumpDirection', itemgetter(0), 0.0),
    Rule('$EditElement', '$JpAmount', itemgetter(0), 0.0),


    Rule('$JpAmount', '?$Num $NumType',
         lambda sems: {'value': (sems[1]['value'], )}, 0.5),
    Rule('$JpAmount', '?$Num $NumType $AdditionalNum',
         lambda sems: {'value': ((sems[1]['value'], ) + sems[2]['value'])}, 1.0),

    Rule('$AdditionalNum', '?$PreNum $NumType',
         lambda sems: {'value': (sems[1]['value'], )}, 0.5),
    Rule('$AdditionalNum', '?$PreNum $NumType $AdditionalNum',
         lambda sems: {'value': ((sems[1]['value'], ) + sems[2]['value'])}, 1.0),


    Rule('$EditType', 'undo', {'construct': 'undo'}, 1.0),
    Rule('$EditType', 'redo', {'construct': 'redo'}, 1.0),
    Rule('$EditType', 'copy', {'construct': 'copy'}, 1.0),
    Rule('$EditType', 'paste', {'construct': 'paste'}, 1.0),
    Rule('$EditType', 'delete', {'construct': 'delete'}, 1.0),
    Rule('$Change', 'change', {'construct': 'change'}, 1.0),
    Rule('$Change', 'update', {'construct': 'change'}, 1.0),
    Rule('$PreNum', '$To', {}, 0.0),
    Rule('$PreNum', '$Optional', {}, 0.0),

]

struct_name_rules = [
    Rule('$ROOT', '$Declare ?$Determiner $StructNameMention',
         lambda sems: merge_dicts({'request': 'include'}, sems[2]), 1.0),
    Rule('$StructNameMention', '$StructElement', itemgetter(0), 0),
    Rule('$StructNameMention', '$StructElement $StructVarElements',
         lambda sems: merge_dicts(sems[0], sems[1]), 0),

    Rule('$StructElement', '$Struct ?$PreStruct $VariableName',
         lambda sems: merge_dicts({'name': sems[2]}, sems[0]), 0),
    Rule('$StructVarElements', '$PreType ?$Struct $Vars $VarNames',
         lambda sems: merge_dicts(sems[3], sems[1]), 0),

    Rule('$VarNames', '$VariableName $Joins $VarNames',
         lambda sems: {'parameters': (sems[2]['parameters'], )}, 1.2),
    Rule('$VarNames', '$VariableName $VarNames',
         lambda sems:
         {'parameters': (sems[1]['parameters'] + (sems[0], ))}, 0.5),
    Rule('$VarNames', '$VariableName',
         lambda sems:{'parameters': (sems[0],)}, 0),

    Rule('$Struct', 'struct',  {'construct': 'struct'}, 1.0),
    Rule('$Struct', 'structure', {'construct': 'struct'}, 1.0),

    Rule('$PreStruct', 'called', {}, 0.5),
    Rule('$PreStruct', '$PreType $PreStructElem', {}, 0.0),
    Rule('$PreStructElem', 'name ', {}, 0.5),
    Rule('$PreStructElem', '?$Struct $Tag', {}, 0.5),
    Rule('$Vars', 'variable', {}, 0.5),
    Rule('$Vars', 'variables', {}, 0.5),
    Rule('$Tag', 'tag', {}, 0.5),
]

array_index_rules = [
    # Rule('$ROOT', '$ArrRef', lambda sems: {'arr_ref': sems[0]}),
    Rule('$Exp', '$ArrRef', itemgetter(0)),
    Rule('$ArrRef', '$NameMention $IndexMention',
         lambda sems: ('[]', sems[0]['name'], sems[1]['index'])),
    Rule('$ArrRef', '$IndexMention $NameMention',
         lambda sems: ('[]', sems[1]['name'], sems[0]['index'])),
    Rule('$IndexMention', '$Elem $Exp',
         lambda sems: {'index': sems[1]}),
    Rule('$IndexMention', '?$Elem $At ?$Index $Exp',
         lambda sems: {'index': sems[3]}),
    Rule('$IndexMention', '$Of $Exp',
         lambda sems: {'index': sems[1]}, 0.25),
    Rule('$Index', 'index', {}, 0.25),
    Rule('$Index', 'position', {}, 0.25),
    Rule('$At', 'at', {}, 0.25),
    Rule('$Of', 'of', {}, 0.25),
    Rule('$Of', 'sub', {}, 0.25),
    Rule('$Elem', 'element', {}, 0.25),
    Rule('$Elem', 'value', {}, 0.25),
    Rule('$NameMention', '?$Elem $Of $VariableName',
         lambda sems: {'name': ('name', sems[2]['name'])}, 0.25),
    Rule('$NameMention', '$VariableName',
         lambda sems: {'name': ('name', sems[0]['name'])}),
]

rules_1 = decl_rules + dec_constructs + var_name_rules\
     + ptr_rules
rules_2 = func_name_rules + func_param_rules + func_call_rules\
     + add_fn_call_rules
rules_3 = loop_define_rules + loop_init_rules + loop_cond_rules\
     + loop_update_rules
rules_4 = pack_rules + init_rules + data_type_rules + arr_size_rules + \
          cond_rules + exp_rules + return_stmt_rules + if_rules
#    + struct_name_rules
rules_5 = nav_rules + edit_rules + optionals + array_index_rules

rules = rules_1 + rules_2 + rules_3 + rules_4 + rules_5
grammar = Grammar(
    rules=rules,
    annotators=[
        TokenAnnotator(),
        VariableNameAnnotator(),
        NumberAnnotator(),
        PackageTypeAnnotator(),
        PositionalNumberAnnotator(),
        StringTextAnnotator(),
        ScopeVariablesAnnotator(),
    ]
)
