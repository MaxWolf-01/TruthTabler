from Exceptions import InvalidExpressionException
from truth_table import TruthTable, prepare


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
    'EQ': ('EQ', "==", "<->", 'EQUALS')
}


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
            except KeyError:
                pass
        raise InvalidExpressionException("Invalid operator.")


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
    def __init__(self, expr: str, truthTable: TruthTable = None, is_root: bool = False):
        self.TT = truthTable if truthTable else TruthTable(expr)
        if is_root:
            self.expr = prepare(Node(translate_operators(prepare(expr))).get_expression())
            remove_all_double_negations(expr)
        else:
            self.expr = expr

    def solve(self) -> list:
        xS = AtomicExpressionSolver(self.TT)
        while self.expr:
            if len(self.expr) == 1:
                if len(self.expr[0]) != 1:
                    return self.expr[0]  # -->[[result]]
                return [x[0] for x in self.TT.table]  # -> single variable
            elif len(self.expr) in [2, 3]:
                return xS.solve(AtomicExpression(self.expr))
            else:
                def solve_inner_expr(expr):
                    xNode = ExpressionSolver(expr, self.TT, is_root=False)
                    return xNode.solve()

                inner_expr_start_indx, inner_expr_end_idx = get_inner_expr_idx(self.expr)
                inner_expr = get_inner_expr(self.expr, inner_expr_start_indx, inner_expr_end_idx)
                self.expr = self.expr[:inner_expr_start_indx] + self.expr[inner_expr_end_idx + 1:]
                self.expr.insert(inner_expr_start_indx, solve_inner_expr(inner_expr))


def translate_operators(expr):
    """
    turns user input operators into keys of OPERATORS / the function names
    """
    translated_expr = []
    for i, x in enumerate(expr):
        for key in OPERATORS:
            if x in OPERATORS[key]:
                translated_expr.append(key)
                break
        if len(translated_expr) != i + 1:
            translated_expr.append(x)
    return translated_expr


def remove_all_double_negations(expr):
    i = 0
    while i + 1 < len(expr):
        if expr[i] == 'NOT' == expr[i + 1]:
            expr.pop(i)
            expr.pop(i)
            i += 1
        i += 1


def get_inner_expr(expr, start, stop):
    return expr[start + 1: stop]


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


def get_bracket_idxs(expr):
    return [i for i, x in enumerate(expr) if isinstance(x, str) and x in '()']


class Node:
    def __init__(self, expr):
        self.left = None
        self.right = None
        self.var_ = None
        self.operator_idx = None
        self.operator = None
        self.add_children(expr)

    def add_children(self, expr: list):
        no_brackets = list(filter(lambda x: x not in "()", expr))
        if len(no_brackets) == 1:
            self.var_ = no_brackets[0]
            return
        elif len(no_brackets) == 0:
            del self
            return
        expr = remove_redundant_brackets(expr)
        self.operator_idx = get_last_operator(expr)
        self.operator = expr[self.operator_idx]
        if expr[:self.operator_idx]:
            self.left = Node(expr[:self.operator_idx])
        if expr[self.operator_idx + 1:]:
            self.right = Node(expr[self.operator_idx + 1:])

    def get_expression(self):
        expr = ''
        if self.is_not_None(self.left):
            expr += '('
            expr += self.left.get_expression()
        if self.operator_idx is not None:
            if self.operator == 'NOT':
                expr += '('
            expr += f" {self.operator} "
        if self.is_not_None(self.right):
            expr += self.right.get_expression()
            expr += ')'
        if self.var_:
            expr += f"{self.var_}"
        return expr

    @staticmethod
    def is_not_None(node):
        return node and (node.operator or node.var_)

    def print(self):
        # just for showing the structure of the tree. Can be impr(remo)oved.
        if self.operator_idx is not None:
            print(self.operator)
        if self.left:
            print('RIGHT:')
            self.left.print()
        if self.right:
            print('LEFT:')
            self.right.print()
        if self.var_:
            print(self.var_)


def remove_redundant_brackets(expr):
    if expr.count('(') != expr.count(')'):
        # ((NOT A OR B) => NOT A OR B  (can happen in parsing process)
        return list(filter(lambda x: x not in "()", expr))
    return remove_redundant_outer_brackets(expr)


def remove_redundant_outer_brackets(expr):
    while expr.__contains__('(') and len(get_expression_levels(expr)) == 1:
        # ((A AND B)) => A AND B
        expr = remove_outer_brackets(expr)
    return expr


def remove_outer_brackets(expr):
    return expr[1: len(expr) - 1]


def get_last_operator(expr):
    expr_levels = get_expression_levels(expr)
    lowest_level_idx = expr_levels[min(expr_levels)]
    lowest_level = [expr[i] for i in lowest_level_idx]
    operator_keys = list(OPERATORS)
    try:
        last_operator = operator_keys[
            max([operator_keys.index(op) for op in get_operators(lowest_level)])
        ]
    except ValueError:
        raise InvalidExpressionException("Invalid operator.")
    last_operator_idx = lowest_level_idx[lowest_level.index(last_operator)]
    return last_operator_idx


def get_expression_levels(expr):
    """
    :returns: dictionary with the level of depth of each part of the expression. Brackets are ignored in the result.
    e.g.: ['A', 'OR', 'B', 'AND', '(', 'A', 'IF', '(', 'NOT', 'C', 'IF', 'D', ')', ')']
    => {0: [0, 1, 2, 3], 1: [5, 6], 2: [8, 9, 10, 11]}
    """
    level = 0
    levels = dict()
    for i, x in enumerate(expr):
        if x == '(':
            level += 1
        elif x == ')':
            level -= 1
        else:
            levels.setdefault(level, []).append(i)
    return levels


def get_operators(expr):
    return [x for x in expr if x in OPERATORS]


def main():
    in_ = input('Expression: ')
    xTree = ExpressionSolver(in_, is_root=True)
    print(in_)
    print(xTree.solve())


if __name__ == '__main__':
    main()
