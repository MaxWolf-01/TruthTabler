# TODO generic unifying of expression...
from bool_expressions import Node
from normal_forms import _CONJUNCTION, _DISJUNCTION, _NOT
from truth_table import getVariables

_NAND = '↑'
_NOR = '↓'


class LogicGateMaker:
    def __init__(self, operator, expr= None,):
        self.operator = operator
        self.gate_expression = None
        if expr:
            self.get_gate_expression(expr)

    def get_gate_expression(self, expr):
        uniform_expr = expr
        if self.contains_only_NOT(expr):
            uniform_expr = expr
        elif self.contains_different_operators(expr):
            operator = 'AND' if self.operator == _CONJUNCTION else 'OR'
            uniform_expr = globals()[f'normal_form_to_{operator}'](expr)
        uniform_expr = remove_double_negations(uniform_expr)
        uniform_expr = Node(uniform_expr).get_expression_as_lists()
        uniform_expr = self.put_variables_out_of_lists(uniform_expr)
        self.gate_expression = self.create_NAND_NOR(uniform_expr)
        return self.gate_expression

    @staticmethod
    def contains_only_NOT(expr):
        return _DISJUNCTION not in expr and _CONJUNCTION not in expr

    def contains_different_operators(self, expr):
        return (_DISJUNCTION in expr and _CONJUNCTION in expr) or self.operator not in expr

    @staticmethod
    def put_variables_out_of_lists(expr):
        string_expr = f"{expr}".replace("\'", '"', -1)
        vars_ = getVariables(LogicGateMaker.list_expr_to_string(string_expr))
        for var in vars_:
            string_expr = string_expr.replace(f'["{var}"]', f'"{var}"', -1)
        return eval(string_expr)

    @staticmethod
    def list_expr_to_string(expr_):
        expr_ = expr_.replace('[', '(', -1)
        expr_ = expr_.replace(']', ')', -1)
        expr_ = expr_.replace(',', '', -1)
        expr_ = expr_.replace('"', '', -1)
        return expr_

    def create_NAND_NOR(self, uniform_expression):
        sign = globals()[f'_N{self.operator}']

        def convert(expr):
            converted_expr = ""
            invert = False
            for i, x in enumerate(expr):
                if isinstance(x, list):
                    converted_expr += convert(x)
                elif len(x) == 1:
                    converted_expr += f' {x} '
                elif x != 'NOT':
                    invert = True
                    converted_expr += f'{sign}'
                else:
                    if len(expr[i + 1]) == 1:
                        invert = True
            if invert:
                converted_expr = f'({converted_expr}{sign}{converted_expr})'
            return converted_expr

        return convert(uniform_expression)


class NandMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__(_CONJUNCTION, normal_form)


class NorMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__(_DISJUNCTION, normal_form)


def normal_form_to_AND(expr: str):
    if expr.__contains__(')' + _CONJUNCTION):  # CCNF
        return de_morgan_inner(expr)
    elif expr.__contains__(')' + _DISJUNCTION):  # CDNF
        return de_morgan_outer(expr)
    else:
        raise Exception('Invalid expression. Must be NormalForm.')


def normal_form_to_OR(expr: str):
    if expr.__contains__(')' + _CONJUNCTION):  # CCNF
        return de_morgan_outer(expr)
    elif expr.__contains__(')' + _DISJUNCTION):  # CDNF
        return de_morgan_inner(expr)
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
    return f'{_NOT}(' + expr + ')'


def unify_operators(expr, inner=True):
    junctions = [_CONJUNCTION, _DISJUNCTION]
    if inner and expr.find(_DISJUNCTION) < expr.find(_CONJUNCTION) or \
            not inner and expr.find(_DISJUNCTION) > expr.find(_CONJUNCTION):
        junctions.reverse()
    expr = expr.replace(*junctions, -1)
    return expr


def negate_vars(expr):
    for var in getVariables(expr):
        expr = expr.replace(var, _NOT + var, -1)
    return expr


def negate_open_brackets(expr):
    return expr.replace('(', f'{_NOT}(', -1)


def remove_double_negations(expr: str):
    return expr.replace(_NOT + _NOT, '', -1)


# xx = NandMaker()
# print(xx.get_gate_expression("(¬A·¬B)+(A·B)"))
# print(xx.get_gate_expression(" ¬(A·B)·¬(A·¬B)·¬(¬A·¬B)"))
# print(xx.get_gate_expression("(A·B)"))
# print(xx.get_gate_expression(" ¬(¬(A·(A·¬B))"))
# print(xx.get_gate_expression("(A·E)+(A·¬D)+(¬A·¬C·D·¬E)+(B·C·¬D)+(B·C·E)+(¬A·¬B·D·¬E)"))
# print(xx.get_gate_expression(f'P{_DISJUNCTION}(S{_DISJUNCTION} {_NOT} R)'))


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
#
#                          should b nand      (((A↓B) ↓ (A ↓ (B↓B))) ↓ ((A↓B) ↓ (A ↓ (B↓B))) ↓ (((A↓A) ↓ (B↓B)))) ↓
#                                             (((A↓B) ↓ (A ↓ (B↓B))) ↓ ((A↓B) ↓ (A ↓ (B↓B))) ↓ (((A↓A) ↓ (B↓B))))
#                                             (¬A·¬B)+(A·B) CDNF
#                                             ¬(A+B)+¬(¬A+¬B) CDNF sao. # CDNF to OR -> demorgan inner
#                                             ¬(¬(¬A·¬B)·¬(A·B)) CDNF sao. # CDNF to AND -> demorgan outer
