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
        return [('$VariableName', '_'.join(tokens))]


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
