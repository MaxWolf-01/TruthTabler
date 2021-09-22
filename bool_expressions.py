from truth_table import TruthTable


def NOT(p):
    return 0 if p else 1  # simple 'not p' would return True instead of 1..


def AND(p, q):
    return p and q


def OR(p, q):
    return p or q


def XOR(p, q):
    return 1 if p != q else 0


def IF(p, q):
    return q if p else 1


def EQ(p, q):
    return 1 if p == q else 0


def nEQ(p, q):
    return 1 if p != q else 0


_OPERATORS = {
    'NOT': ("~", "NOT", "!"),
    'AND': ("AND", "&&"),
    'OR': ("OR", "||"),
    'XOR': ("XOR",),
    'IF': ("->", "IF"),
    'EQ': ("==", "<->", 'EQ'),
    'nEQ': ("!=", "nEQ")
}


class AtomicExpression:
    """
    takes an Expression of the form "['var1', '(_OPERATOR)', 'var2']" or "['NOT',  'var1']" and figures out
    the operators and variables
    """

    def __init__(self, expression: list):
        self.operator, self.variables = self.get_operator_and_vars(expression)

    @staticmethod
    def get_operator_and_vars(expression):  # -> tuple[function, list]:
        if expression[0] == 'NOT':
            return NOT, expression[1:]
        elif len(expression) == 3:
            return globals()[expression.pop(1)], expression
        raise Exception("Invalid expression(Invalid Operator): ")


class ExpressionSolver:
    """
    takes an atomicExpression to evalutate it + a TruthTable to look up values of variable names
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
            for i in range(len(val1)):
                result.append(f(val1[i], val2[i]))
        else:
            val1 = values[0]
            for val in val1:
                result.append(f(val))
        return result

    def getValues(self):
        values = []
        for var in self.expr.variables:
            if type(var) is not list:
                values.append([row[self.TT.variables.index(var)] for row in self.TT.table])
            else:
                values.append(var)
        return values

    def set_atomic_expr(self, a_expr):
        if a_expr is not None:
            self.expr = a_expr


class ExpressionTree:
    def __init__(self, expr: list, truthTable: TruthTable, is_root: bool):
        self.expr = expr
        self.TT = truthTable
        if is_root:
            self.expr = self.translateOperators()

    def solve(self) -> list:
        xS = ExpressionSolver(self.TT)
        while self.expr:
            if len(self.expr) == 1:  # -->[[result]]
                return self.expr[0]
            elif len(self.expr) == 3 or len(self.expr) == 2:
                return xS.solve(AtomicExpression(self.expr))
            elif not self.expr.__contains__('('):
                operators = []
                idx = 0
                while idx < len(self.expr):
                    if self.expr[idx] == 'NOT':
                        self.expr.insert(idx, xS.solve(AtomicExpression([self.expr.pop(i) for i in [idx, idx]])))
                        idx += 1
                    else:
                        if self.expr[idx] in list(_OPERATORS.keys()):
                            operators.append(self.expr[idx])
                        idx += 1
                first_operator = list(_OPERATORS.keys())[
                    min([list(_OPERATORS.keys()).index(op) for op in operators])
                ]
                first_op_idx = self.expr.index(first_operator)
                result = xS.solve(AtomicExpression([self.expr.pop(i) for i in [first_op_idx - 1] * 3]))
                self.expr.insert(first_op_idx - 1, result)
            else:
                def solve_inner_expr(expr):
                    xTree = ExpressionTree(expr, self.TT, False)
                    return xTree.solve()

                bracket_idxs = [i for i in range(len(self.expr)) if self.expr[i] in '()']
                open_brackets = 0
                closed_brackets = 0
                for i in bracket_idxs:
                    if self.expr[i] == '(':
                        open_brackets += 1
                    elif self.expr[i] == ')':
                        closed_brackets += 1
                        if open_brackets == closed_brackets:
                            inner_expr = self.expr[
                                         bracket_idxs[0] + 1: bracket_idxs[open_brackets + closed_brackets - 1]]
                            solved_inner_expr = solve_inner_expr(inner_expr)
                            self.expr = self.expr[:bracket_idxs[0]] + \
                                        self.expr[bracket_idxs[open_brackets + closed_brackets-1]+1:]
                            self.expr.insert(bracket_idxs[0], solved_inner_expr)

    def translateOperators(self):
        """
        turns user input operators into keys of _OPERATORS / their function names
        """
        translated_expr = []
        for x in self.expr:
            for key in _OPERATORS.keys():
                if x in _OPERATORS[key]:
                    translated_expr.append(key)
                else:
                    translated_expr.append(x)
                break
        return translated_expr
