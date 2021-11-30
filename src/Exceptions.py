from operator_symbols import OPERATORS


class BracketException(Exception):
    def __init__(self, expr, msg):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {msg[0]} != {msg[1]} '
                                        f'for: "{expr}"')


class InvalidExpressionException(Exception):
    def __init__(self, msg):
        super(InvalidExpressionException, self).__init__(f'Invalid expression: {msg}')


class InvalidOperatorException(InvalidExpressionException):
    def __init__(self, operator=''):
        nl = '\n'
        info = f"Invalid operator in expression '{operator}'.\nSupported operators are:\n" \
               f"{nl.join(str(OPERATORS[k]) for k in OPERATORS)}"
        super(InvalidOperatorException, self).__init__(info)
