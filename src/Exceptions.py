class BracketException(Exception):
    def __init__(self, expr, msg):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {msg[0]} != {msg[1]} '
                                        f'for: "{expr}"')


class InvalidExpressionException(Exception):
    def __init__(self, msg):
        super(InvalidExpressionException, self).__init__(f'Invalid expression: {msg}')

