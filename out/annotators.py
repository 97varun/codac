from word2number import w2n


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
        if len(tokens) == 1:
            if tokens[0] in ['int', 'integer', 'double', 'float', 'char',
                             'character']:
                val = tokens[0]
                if val == 'integer':
                    val = 'int'
                elif val == 'character':
                    val = 'char'
                return [('$DataType', val)]
        elif len(tokens) == 2:
            if tokens[0] in ['long', 'short'] and\
               tokens[1] in ['int', 'integer']:
                val = tokens[1]
                if val == 'integer':
                    val = 'int'
                return [('$DataType', tokens[0] + ' ' + val)]
        return []


class VariableNameAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) > 0 and tokens[0] == 'pointer':
            return [('$VariableName', '*' + '_'.join(tokens[1:]))]
        if len(tokens) > 0 and tokens[0] == 'address':
            if len(tokens) > 1 and tokens[1] == 'of':
                res_words = ['variable', 'function', 'array', 'int', 'integer',
                             'double', 'float', 'char', 'character']
                if len(tokens) > 2 and  tokens[2] in res_words:
                    return [('$VariableName', '&' + '_'.join(tokens[3:]))]
            return [('$VariableName', '&' + '_'.join(tokens[2:]))]

        return [('$VariableName', '_'.join(tokens))]

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
        return [('$StringText', ' '.join(tokens))]

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
        if len(tokens) == 1:
            if tokens[0] in PosNumbers:
                val = PosNumbers.index(tokens[0]) + 1
                return [('$PosNum', val)]
        return []


class StringNumberAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) <= 4:
            types = [int, float]
            try:
                if (type(w2n.word_to_num(' '.join(tokens))) in types):
                    val = w2n.word_to_num(' '.join(tokens))
                    # print(val)
                    return [('$StrNumber', val)]
            except ValueError:
                pass
        return []
