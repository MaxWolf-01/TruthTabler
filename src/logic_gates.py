import truth_table
from truth_tabler import _CONJUNCTION, _DISJUNCTION


class NandMaker:
    def __init__(self, normal_form):
        self.variables = truth_table.getVariables(normal_form)
        self.AND_expression = normal_form_to_AND(normal_form)
        self.NAND = None  # todo


class NorMaker:
    def __init__(self, normal_form):
        self.variables = truth_table.getVariables(normal_form)
        self.OR_expression = normal_form_to_OR(normal_form)
        self.NOR = None  # todo


def normal_form_to_AND(expr: str):
    if expr.__contains__(')' + _CONJUNCTION):
        de_morgan_inner(expr)
    elif expr.__contains__(')' + _DISJUNCTION):
        de_morgan_outer(expr)
    else:
        raise Exception('Invalid expression. Must be NormalForm.')


def normal_form_to_OR(expr: str):
    if expr.__contains__(')' + _CONJUNCTION):
        de_morgan_outer(expr)
    elif expr.__contains__(')' + _DISJUNCTION):
        de_morgan_inner(expr)
    else:
        raise Exception('Invalid expression. Must be NormalForm.')


def de_morgan_inner(expr):
    expr = negate_open_brackets(expr)
    expr = negate_vars(expr)
    expr = unify_operators(expr)
    return expr


def de_morgan_outer(expr):
    expr = negate_open_brackets(expr)
    expr = unify_operators(expr, inner=False)
    return '¬(' + expr + ')'


def unify_operators(expr, inner=True):
    junctions = [_CONJUNCTION, _DISJUNCTION]
    if inner and expr.find(_DISJUNCTION) < expr.find(_CONJUNCTION) or \
            not inner and expr.find(_DISJUNCTION) > expr.find(_CONJUNCTION):
        junctions.reverse()
    expr = expr.replace(*junctions, -1)
    return expr


def negate_vars(expr):
    expr_list = truth_table.prepare(expr)
    for var in truth_table.getVariables(expr_list):  # todo expr
        expr = expr.replace(var, '¬' + var, -1)
    return expr


def negate_open_brackets(expr):
    return expr.replace('(', '¬(', -1)


def remove_double_negations(expr: str):
    return expr.replace('¬¬', '', -1)


# from truth_tabler import TruthTabler
#
# tabler = TruthTabler()
# x1 = '(¬A+¬B)·(¬A+B)·(A+B)'
# x2 = '(¬A+¬B)·(¬A+B)·(A+B)'
# print(tabler.evaluate(remove_double_negations(de_morgan_outer(x1))) == tabler.evaluate(x1))
# print(tabler.evaluate(remove_double_negations(de_morgan_inner(x2))) == tabler.evaluate(x2))

#                                             (¬A+¬B)·(¬A+B)·(A+B) # CCNF
#                                            ¬(¬(¬A+¬B)+¬(¬A+B)+¬(A+B)) same as above  # CCNF to OR -> demorgan outer
#                                            ¬(A·B)·¬(A·¬B)·¬(¬A·¬B) same as above # CCNF to AND -> demorgan inner
#                                             (¬A·¬B)+(A·B) CDNF
#                                             ¬(A+B)+¬(¬A+¬B) CDNF sao. # CDNF to OR -> demorgan inner
#                                             ¬(¬(¬A·¬B)·¬(A·B)) CDNF sao. # CDNF to AND -> demorgan outer
