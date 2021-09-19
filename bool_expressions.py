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
    takes an atomicExpression to evalutate it
    """

    def __init__(self, truthTable: TruthTable, atomic_expr: AtomicExpression = None):
        self.expr = atomic_expr
        self.TT = truthTable

    def solve(self, atomic_expr=None) -> list:
        self.set_atomic_expr(atomic_expr)
        result = []
        f = self.expr.operator
        p_q = self.getValues()
        if len(p_q) == 2:
            p, q = p_q
            for i in range(len(p)):
                result.append(f(p[i], q[i]))
        else:
            p = p_q[0]
            for val in p:
                result.append(f(val))
        return result

    def getValues(self):
        vars_ = []
        for var in self.expr.variables:
            if type(var) is not list:
                vars_.append([row[self.TT.variables.index(var)] for row in self.TT.table])
            else:
                vars_.append(var)
        return vars_

    def set_atomic_expr(self, a_expr):
        if a_expr is not None:
            self.expr = a_expr


class ExpressionTree:
    def __init__(self, expr: list, truthTable: TruthTable, is_root: bool):
        self.expr = expr
        self.TT = truthTable
        if is_root:
            self.translateOperators()

    def solve(self) -> list:
        xS = ExpressionSolver(self.TT)
        while self.expr:
            if len(self.expr) == 1:  # [[result]]
                return self.expr[0]
            elif len(self.expr) == 3 or len(self.expr) == 2:
                return xS.solve(AtomicExpression(self.expr))
            elif not self.expr.__contains__('('):
                operators = []
                for i in range(len(self.expr)):
                    if self.expr[i] == 'NOT':
                        self.expr.insert(i, xS.solve(AtomicExpression([self.expr.pop(i) for i in [i, i]])))
                        i += 1
                    else:
                        if self.expr[i] in list(_OPERATORS.keys()):
                            operators.append(self.expr[i])

                first_operator = list(_OPERATORS.keys())[min([list(_OPERATORS.keys())
                                                             .index(op) for op in operators])]
                first_op_idx = self.expr.index(first_operator)
                result = xS.solve(AtomicExpression([self.expr.pop(i) for i in [first_op_idx-1]*3]))
                self.expr.insert(first_op_idx-1, result)
            else:
                for i in range(len(self.expr)):
                    if self.expr[i] == '(':
                        inner_expr = []
                        for _ in range(i, len(self.expr)):
                            if self.expr[i+1] == ')':
                                self.expr = self.expr[i+2:] + self.expr[:i]  # remove brackets
                                xTree = ExpressionTree(inner_expr, self.TT, False)
                                self.expr.insert(i, xTree.solve())
                                break
                            inner_expr.append(self.expr.pop(i+1))
                        if inner_expr:
                            break

    def translateOperators(self):
        """
        turns user input operators into keys of _FUNCTIONS
        """
        translated = []
        for x in self.expr:
            for key in _OPERATORS.keys():
                if x in _OPERATORS[key]:
                    translated.append(key)
                else:
                    translated.append(x)
        return translated
