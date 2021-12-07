from operator_symbols import OPERATORS


class TablerException(Exception):
    def __init__(self, msg=''):
        super(TablerException, self).__init__(msg)


class BracketException(TablerException):
    def __init__(self, expr, msg):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {msg[0]} != {msg[1]} '
                                        f'for: "{expr}"')


class InvalidExpressionException(TablerException):
    def __init__(self, msg):
        super(InvalidExpressionException, self).__init__(f'Invalid expression: {msg}')


class InvalidOperatorException(InvalidExpressionException):
    def __init__(self, operator=''):
        nl = '\n'
        info = f"\nInvalid operator in expression '{operator}'.\nSupported operators are:\n" \
               f"{nl.join(str(OPERATORS[k]) for k in OPERATORS)}\n"
        super(InvalidOperatorException, self).__init__(info)
