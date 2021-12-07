from Exceptions import InvalidExpressionException, InvalidOperatorException
from parsing import parse_expr_to_list, _translate_operators
from truth_table import TruthTable


def NOT(p):
    return 0 if p else 1  # simple 'not p' would return True instead of 1..


def AND(p, q):
    return p and q


def OR(p, q):
    return p or q


def NAND(p, q):
    return 1 if not p or not q else 0


def NOR(p, q):
    return 1 if not p and not q else 0


def XOR(p, q):
    return 1 if p != q else 0


def IF(p, q):
    return q if p else 1


def EQ(p, q):
    return 1 if p == q else 0


class AtomicExpression:
    """
    takes an Expression of the form "['var1', 'OPERATOR', 'var2']" or "['NOT',  'var1']" and figures out
    the operators and variables
    """

    def __init__(self, expression: list):
        self.operator, self.variables = self.get_operator_and_vars(expression)

    @staticmethod
    def get_operator_and_vars(expression):  # -> tuple[function, list]:
        if expression[0] == 'NOT':
            return NOT, expression[1:]
        elif len(expression) == 3:
            try:
                return globals()[expression.pop(1)], expression
            except KeyError as e:
                raise InvalidOperatorException(e.args[0])


class AtomicExpressionSolver:
    """
    takes an AtomicExpression to evalutate it + a TruthTable to look up values of variable names
    """

    def __init__(self, truthTable: TruthTable, atomic_expr: AtomicExpression = None):
        self.expr = atomic_expr
        self.TT = truthTable

    def solve(self, atomic_expr: AtomicExpression = None) -> list:
        self.set_atomic_expr(atomic_expr)
        result = []
        f = self.expr.operator
        values = self.getValues()
        if len(values) == 2:
            val1, val2 = values
            for p, q in zip(val1, val2):
                result.append(f(p, q))
        else:
            val1 = values[0]
            for p in val1:
                result.append(f(p))
        return result

    def getValues(self):
        values = []
        for var in self.expr.variables:
            if not isinstance(var, list):
                if var == '1':
                    values.append([1] * len(self.TT.table))
                elif var == '0':
                    values.append([0] * len(self.TT.table))
                else:
                    try:
                        values.append([row[self.TT.variables.index(var)] for row in self.TT.table])
                    except ValueError:
                        raise InvalidExpressionException(f'Invalid variable: {var} (Must be a single letter!)')
            else:
                values.append(var)
        return values

    def set_atomic_expr(self, a_expr):
        if a_expr is not None:
            self.expr = a_expr


class ExpressionSolver:
    """
    takes an expression parsed by the Node class and solves from most nested equation to the least.
    """
    def solve(self, expr, is_root=True, TT: TruthTable = None) -> list:
        if is_root:
            TT = TT if TT else TruthTable(expr)
            expr = self._prepare_expression(expr)
        xS = AtomicExpressionSolver(TT)
        expression = []
        if len(expr) == 1 and len(expr[0]) == 1:
            return TT.table
        for i, x in enumerate(expr):
            if self._has_double_negation(expr, i):
                expression = self.solve(expr[i + 1][1], is_root=False, TT=TT)
            elif isinstance(x, list):
                expression.append(self.solve(x, is_root=False, TT=TT))
            else:
                expression.append(x)
        return xS.solve(AtomicExpression(expression))

    @staticmethod
    def _prepare_expression(expr):
        if not isinstance(expr, list):
            expr = parse_expr_to_list(expr)
        else:
            expr = _translate_operators(expr)
        return expr

    @staticmethod
    def _has_double_negation(expr, i):
        return expr[i] == 'NOT' and isinstance(expr[i + 1], list) and expr[i + 1][0] == 'NOT'


def main():
    xTree = ExpressionSolver()
    while True:
        in_ = input('Expression: ')
        print(in_)
        print(xTree.solve(in_))


if __name__ == '__main__':
    main()
