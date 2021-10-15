from src.truth_table import TruthTable


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


OPERATORS = {
    'NOT': ("NOT", "!", '¬', '-'),
    'AND': ("AND", "&&", '&', '·', '∧'),
    'OR': ("OR", "||", '+', '∨'),
    'NAND': ('NAND',),
    'NOR': ('NOR',),
    'XOR': ("XOR",),
    'IF': ("IF", "->", '=>', '>'),
    'EQ': ('EQ', "==", "<->", '<=>')
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
            try:
                return globals()[expression.pop(1)], expression
            except KeyError:
                pass
        raise InvalidExpressionException("Invalid operator. Or redundant parentheses around single variable.")


class AtomicExpressionSolver:
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
                if var == '1':
                    values.append([1]*len(self.TT.table))
                elif var == '0':
                    values.append([0]*len(self.TT.table))
                else:
                    try:
                        values.append([row[self.TT.variables.index(var)] for row in self.TT.table])
                    except ValueError:
                        raise InvalidExpressionException(f'Invalid Operator: {var}')
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
        if self.TT.variables is None:
            raise InvalidExpressionException
        if is_root:
            self.expr = self.translate_operators()
            self.remove_double_negations()

    def solve(self) -> list:
        xS = AtomicExpressionSolver(self.TT)
        while self.expr:
            if len(self.expr) == 1:
                if len(self.expr[0]) == 1:
                    return [x[0] for x in self.TT.table]  # -> single variable
                elif type(self.expr[0]) != list:
                    raise InvalidExpressionException(self.expr[0])
                return self.expr[0]  # -->[[result]]
            elif len(self.expr) == 3 or len(self.expr) == 2:
                if self.remove_redundant_parentheses_from_single_var():
                    continue
                return xS.solve(AtomicExpression(self.expr))
            elif not self.expr.__contains__('('):
                self.solve_all_NOT(xS)
                highest_priority_operator_idx = self.get_highest_priority_operator_idx(self.get_operators())
                highest_priority_expression = [self.expr.pop(i) for i in [highest_priority_operator_idx - 1] * 3]
                result = xS.solve(AtomicExpression(highest_priority_expression))
                self.expr.insert(highest_priority_operator_idx - 1, result)
            else:
                def solve_inner_expr(expr):
                    xTree = ExpressionTree(expr, self.TT, is_root=False)
                    return xTree.solve()

                bracket_idxs = get_bracket_idxs(self.expr)
                inner_expr_start_indx, inner_expr_end_idx = get_inner_expr_idx(self.expr)
                inner_expr = self.expr[inner_expr_start_indx + 1: inner_expr_end_idx]
                solved_inner_expr = solve_inner_expr(inner_expr)
                self.expr = self.expr[:inner_expr_start_indx] + self.expr[inner_expr_end_idx+1:]
                self.expr.insert(bracket_idxs[0], solved_inner_expr)

    def translate_operators(self):
        """
        turns user input operators into keys of OPERATORS / their function names
        """
        translated_expr = []
        for i in range(len(self.expr)):
            for key in OPERATORS.keys():
                if self.expr[i] in OPERATORS[key]:
                    translated_expr.append(key)
                    break
            if len(translated_expr) != i + 1:
                if self.var_is_valid(self.expr[i]):
                    translated_expr.append(self.expr[i])
        return translated_expr

    @staticmethod
    def var_is_valid(var):
        if len(var) == 1:
            return True
        else:
            raise InvalidExpressionException(f"Invalid variable {var}")

    def remove_redundant_parentheses_from_single_var(self):
        if len(self.expr) == 3 and len(self.expr[1]) == 1:
            self.expr.pop(0)
            self.expr.pop(1)
            return True

    def solve_all_NOT(self, expressionSolver: AtomicExpressionSolver):
        i = 0
        while i < len(self.expr):
            if self.expr[i] == 'NOT':
                self.expr.insert(i, expressionSolver.solve(AtomicExpression([self.expr.pop(idx) for idx in [i, i]])))
                i += 1
            i += 1

    def get_operators(self):
        return [x for x in self.expr if x in list(OPERATORS.keys())]

    def get_highest_priority_operator_idx(self, operators):
        first_operator = list(OPERATORS.keys())[
            min([list(OPERATORS.keys()).index(op) for op in operators])
        ]
        return self.expr.index(first_operator)

    def remove_double_negations(self):
        i = 0
        while i+1 < len(self.expr):
            if self.expr[i] == 'NOT' == self.expr[i+1]:
                self.expr.pop(i)
                self.expr.pop(i)
                i += 1
            i += 1


def get_bracket_idxs(expr):
    return [i for i in range(len(expr)) if type(expr[i]) == str and expr[i] in '()']


def get_inner_expr_idx(expr):
    """
    :return: start and end index of inner expression including brackets
    """
    open_brackets = 0
    closed_brackets = 0
    bracket_idxs = get_bracket_idxs(expr)
    for i in bracket_idxs:
        if expr[i] == '(':
            open_brackets += 1
        elif expr[i] == ')':
            closed_brackets += 1
            if open_brackets == closed_brackets:
                inner_expr_start_idx = bracket_idxs[0]
                inner_expr_end_idx = bracket_idxs[(open_brackets + closed_brackets) - 1]
                return inner_expr_start_idx, inner_expr_end_idx


class InvalidExpressionException(Exception):
    def __init__(self, msg):
        super(InvalidExpressionException, self).__init__(f'Invalid expression: {msg}')
