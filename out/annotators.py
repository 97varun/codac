from word2number import w2n
from exec import get_scope_variables


class Annotator:
    """A base class for annotators."""
    def annotate(self, tokens):
        """Returns a list of pairs, each a category
        and a semantic representation."""
        return []


class TokenAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) == 1:
            return [('$Token', tokens[0])]
        else:
            return []


class DataTypeAnnotator(Annotator):
    def annotate(self, tokens):
        types = [
            'int', 'integer',
            'short', 'short int',
            'long', 'long int', 'long double',
            'long long', 'long long int',
            'char', 'character',
            'float', 'double',
        ]
        if len(tokens) <= 3 and len(tokens) > 0:
            typ = ' '.join(tokens)
            typ = typ.replace('character', 'char')
            typ = typ.replace('integer', 'int')
            if typ in types:
                return [('$DataType', typ)]
        return []


class VariableNameAnnotator(Annotator):
    def annotate(self, tokens):
        return [('$VarName', '_'.join(tokens))]


class ScopeVariablesAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) > 0:
            scope_variables = get_scope_variables()
            if '_'.join(tokens) in scope_variables:
                return [('$ScopeVariable', '_'.join(tokens))]
        return []


class StringTextAnnotator(Annotator):
    def annotate(self, tokens):
        mods = ['mod', 'modulus']
        for x in mods:
            while(len(tokens) > 0 and x in tokens):
                try:
                    idx = tokens.index(x)
                    if (idx < len(tokens) - 1):
                        del tokens[idx]
                        tokens[idx] = '%' + tokens[idx]
                    else:
                        tokens[idx] = '%'
                except ValueError:
                    pass
        string_text = ' '.join(tokens)
        string_text = string_text.replace('newline', '\\n')
        string_text = string_text.replace('new line', '\\n')
        return [('$StringText', string_text)]


class NumberAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) == 1:
            try:
                value = float(tokens[0])
                if int(value) == value:
                    value = int(value)
                return [('$Number', value)]
            except ValueError:
                pass
        types = [int, float]
        try:
            val = w2n.word_to_num(' '.join(tokens))
            # if w2n.word_to_num(' '.join(tokens[1:])) == val or\
            #         w2n.word_to_num(' '.join(tokens[:-1])) == val:
            #     return []
            if type(val) in types:
                return [('$Number', val)]
        except ValueError:
            pass
        return []


class PackageTypeAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) == 1:
            if tokens[0] in ['stdlib', 'stdio', 'string', 'time',
                             'stdbool', 'stdarg', 'math']:
                return[('$PackageName', tokens[0])]
        return []


class PositionalNumberAnnotator(Annotator):
    def annotate(self, tokens):
        PosNumbers = ['first', 'second', 'third', 'fourth', 'fifth',
                      'sixth', 'seventh', 'eighth', 'nineth', 'tenth']
        RomanNumbers = ['first', 'ii', 'iii', 'iv', 'v',
                        'vi', 'vii', 'viii', 'ix', 'x']
        if len(tokens) == 1:
            if tokens[0] in PosNumbers:
                val = PosNumbers.index(tokens[0]) + 1
                return [('$PosNum', val)]
            if tokens[0] in RomanNumbers:
                val = RomanNumbers.index(tokens[0]) + 1
                return [('$PosNum', val)]
        return []


# No longer used
class VarNameAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) > 0 and tokens[0] == 'pointer':
            return [('$VarName', '*' + '_'.join(tokens[1:]))]
        if len(tokens) > 0 and tokens[0] == 'address':
            if len(tokens) > 1 and tokens[1] == 'of':
                res_words = ['variable', 'function', 'array', 'integer',
                             'int', 'double', 'float', 'char', 'character']
                if len(tokens) > 2 and tokens[2] in res_words:
                    return [('$VarName', '&' + '_'.join(tokens[3:]))]
            return [('$VarName', '&' + '_'.join(tokens[2:]))]
        return [('$VariableName', '_'.join(tokens))]
