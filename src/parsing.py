from Exceptions import InvalidOperatorException
from operator_symbols import OPERATORS, OPERATOR_SIGNS
from truth_table import split_to_list


def parse_expr_to_list(expr, vars_in_extra_lists=False):
    return Node(expr).get_expression_as_lists(vars_in_extra_lists)


def list_expr_to_string(expr):
    """
    Turns a boolean expression in the form of nested lists back into a string using operator_signs.
    """
    string_expr = ''
    expr = remove_redundant_lists(expr)
    for i, x in enumerate(expr):
        if isinstance(x, list):
            string_expr += list_expr_to_string(x)
        elif len(x) != 1:
            string_expr += OPERATOR_SIGNS[x]
        else:
            string_expr += x
    return f'({string_expr})'


def remove_redundant_lists(x):
    while isinstance(x, list) and len(x) == 1:
        x = x[0]
    return x


class Node:
    """
    Parses a boolean expression in the form of a string into lists of lists, each list containing exactly one operator.
    So the lists are nested in a way that the operations get executed in order:
    e.g.: not A or B and (c if d) => [['NOT', 'A'], 'OR', ['B', 'AND', ['C', 'IF', 'D']]]
    """

    def __init__(self, expr):
        self.left = None
        self.right = None
        self.var_ = None
        self.operator_idx = None
        self.operator = None
        self.create_expr_tree(self.prepare_expr(expr))

    @staticmethod
    def prepare_expr(expr):
        if isinstance(expr, str):
            return _translate_operators(split_to_list(expr))
        return expr

    def create_expr_tree(self, expr: list):
        if self.handle_constants(expr):
            return
        no_brackets = list(filter(lambda x: x not in "()", expr))
        if len(no_brackets) == 1:
            self.var_ = no_brackets[0]
            return
        elif len(no_brackets) == 0:
            del self
            return
        expr = _remove_redundant_brackets(expr)
        self.operator_idx = _get_last_operator(expr)
        self.operator = expr[self.operator_idx]
        if expr[:self.operator_idx]:
            self.left = Node(expr[:self.operator_idx])
        if expr[self.operator_idx + 1:]:
            self.right = Node(expr[self.operator_idx + 1:])

    def handle_constants(self, expr):
        if isinstance(expr, int):
            self.var_ = [expr]
            return True
        return False

    def get_expression_as_string(self):
        expr = ''
        if self.is_not_None(self.left):
            expr += '('
            expr += self.left.get_expression_as_string()
        if self.operator_idx is not None:
            if self.operator == 'NOT':
                expr += '('
            expr += f" {self.operator} "
        if self.is_not_None(self.right):
            expr += self.right.get_expression_as_string()
            expr += ')'
        if self.var_:
            expr += f"{self.var_}"
        return expr

    def get_expression_as_lists(self, vars_in_extra_lists=False):
        #                             variables are only put into extra lists for circuit_creator.py
        expr = []
        if self.is_not_None(self.left):
            expr.append(self.left.get_expression_as_lists(vars_in_extra_lists))
        if self.operator_idx is not None:
            expr.append(self.operator)
            if self.operator == 'NOT' and self.right.var_:
                expr.append(self.right.var_)
                return expr
        if self.is_not_None(self.right):
            expr.append(self.right.get_expression_as_lists(vars_in_extra_lists))
        if self.var_:
            if vars_in_extra_lists:
                expr.append(self.var_)
            else:
                expr = self.var_
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


def _translate_operators(expr):
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


def _remove_redundant_brackets(expr):
    expr_levels = _get_expression_levels(expr)
    if expr.count('(') != expr.count(')') and len(expr_levels) == 1:
        # ((NOT A OR B) => NOT A OR B  (can happen in parsing process) # (NOT(NOT A OR B) => ignored
        return list(filter(lambda x: x not in "()", expr))
    return _remove_redundant_outer_brackets(expr, expr_levels)


def _remove_redundant_outer_brackets(expr, expr_levels):
    while expr.__contains__('(') and len(expr_levels) == 1:
        # ((A AND B)) => A AND B
        expr = _remove_outer_brackets(expr)
    return expr


def _remove_outer_brackets(expr):
    return expr[1: len(expr) - 1]


def _get_last_operator(expr):
    expr_levels = _get_expression_levels(expr)
    lowest_level_idx = expr_levels[min(expr_levels)]
    lowest_level = [expr[i] for i in lowest_level_idx]
    operator_keys = list(OPERATORS)
    try:
        last_operator = operator_keys[
            max([operator_keys.index(op) for op in _get_operators(lowest_level)])
        ]
    except ValueError:
        raise InvalidOperatorException()
    if last_operator == 'NOT':
        idx = min(i for i, x in enumerate(lowest_level) if x == last_operator)
    else:
        idx = max(i for i, x in enumerate(lowest_level) if x == last_operator)
    last_operator_idx = lowest_level_idx[idx]
    return last_operator_idx


def _get_expression_levels(expr):
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


def _get_operators(expr):
    return [x for x in expr if x in OPERATORS]
